import os
import sys
import argparse
import requests
import pandas as pd
import glob
import time

# 让 Python 能够找到 .env 文件 (位于项目根目录)
# 假设脚本在 docs/指标工具箱/AI/ 下，.env 在 ../../../ 下
# 简单起见，从当前执行目录或父目录查找
def load_env_key():
    # 尝试读取 .env 文件的简单实现，不依赖 python-dotenv
    env_paths = [".env", "../../../.env", "docs/指标工具箱/AI/../../../../.env"]
    for path in env_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        return line.strip().split("=", 1)[1]
    return None

API_KEY = load_env_key() or os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ 未找到 GOOGLE_API_KEY，请检查 .env 文件。")
    sys.exit(1)

# Gemini API Endpoint
# Verified stable model for Free Tier: gemini-flash-latest
MODEL_NAME = "gemini-flash-latest"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def get_ai_analysis(system_prompt, data_context):
    headers = {"Content-Type": "application/json"}
    
    # 构造 Prompt
    # 将系统提示词和数据合并发送
    full_prompt = f"""
{system_prompt}

---

### 当前市场数据 (CSV 片段)
(仅提供最近的数据以便分析，请基于此数据进行推演)

{data_context}
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3, # 分析类任务建议低温度
            "maxOutputTokens": 8192
        }
    }
    
    max_retries = 6
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                try:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return text
                except (KeyError, IndexError):
                    print(f"❌ 解析响应失败: {result}")
                    return None
            elif response.status_code == 429:
                print(f"⚠️ 触发频率限制 (429)，等待 {retry_delay} 秒后重试... ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2 # 指数退避
                continue
            else:
                print(f"❌ API 请求失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ 网络请求异常: {e}")
            return None
            
    print("❌ 重试次数耗尽，分析失败。")
    return None

def main():
    parser = argparse.ArgumentParser(description='使用 Gemini AI 分析威科夫行情')
    parser.add_argument('csv_path', help='清洗后的 CSV 数据路径')
    args = parser.parse_args()
    
    csv_path = args.csv_path
    if not os.path.exists(csv_path):
        print(f"❌ 找不到文件: {csv_path}")
        return

    # 1. 准备 Prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "提示词.md")
    if not os.path.exists(prompt_path):
         # 尝试从 args[0] 的位置找
         prompt_path = "docs/指标工具箱/AI/提示词.md"
         
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        print("⚠️ 未找到提示词.md，使用默认简易 Prompt")
        system_prompt = "请对以下威科夫行情数据进行专业分析，识别 SC, AR, ST 等关键事件。"

    # 2. 准备数据
    # [优化] 读取最后 100 行 (大幅减少 Token 消耗，避免 429)
    # Gemini Free Tier limit is strict on RPM and TPM.
    df = pd.read_csv(csv_path)
    
    # 获取基本信息
    base_name = os.path.splitext(os.path.basename(csv_path))[0].replace("_Cleaned", "")
    
    # 截取数据
    recent_data = df.tail(100).to_csv(index=False)
    
    print(f"🧠 正调用 Google Gemini ({MODEL_NAME}) 进行深度分析...")
    print(f"📄 分析对象: {base_name} (数据长度: {len(df)} -> 提交最近 100 行)")

    analysis_text = get_ai_analysis(system_prompt, recent_data)
    
    if analysis_text:
        # 3. 保存报告
        # 注意：这里需要替换掉 ai_analyze.py 生成的报告中的图片路径引用
        # 提示词要求生成图片，但 AI 只生成文本。
        # 我们假设 output 图片已经由 `wyckoff_plot.py` 生成，名为 {base_name}_Wyckoff_Chart.png
        
        # 强制插入图片链接（如果 AI 没生成或生成错了）
        chart_filename = f"{base_name}_Wyckoff_Chart.png"
        img_link = f"![{base_name} Chart](./{chart_filename})"
        
        # 简单的替换/检查逻辑
        # 如果 AI 返回的文本里没有图片链接，我们在前面加一个
        if chart_filename not in analysis_text:
            analysis_text = f"# 威科夫深度分析报告: {base_name}\n\n{img_link}\n\n{analysis_text}"
        
        # 写入文件
        # 输出目录应与 wyckoff_plot.py 保持一致: docs/指标工具箱/AI/output/
        output_dir = "docs/指标工具箱/AI/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = os.path.join(output_dir, f"{base_name}_Wyckoff_Analysis.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(analysis_text)
            
        print(f"✅ AI 分析报告已生成: {output_path}")
    else:
        print("❌ 分析失败，未生成报告。")
        sys.exit(1)

if __name__ == "__main__":
    main()
