
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

# --- 1. 配置中文显示 ---
def configure_font():
    system = platform.system()
    font_path = None
    
    if system == "Darwin":  # macOS
        font_candidates = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc"]
    elif system == "Windows":
        font_candidates = ["C:\\Windows\\Fonts\\msyh.ttc", "C:\\Windows\\Fonts\\simhei.ttf"]
    else:  # Linux
        font_candidates = ["/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"]
    
    for path in font_candidates:
        if os.path.exists(path):
            font_path = path
            break
            
    if font_path:
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
        print(f"✅ 已加载中文字体: {font_path}")
        return prop
    else:
        print("⚠️ 未找到常用中文字体，中文可能乱码")
        return None

font_prop = configure_font()

import argparse
import sys

# --- 2. 读取数据 (动态路径) ---
# 使用 argparse 解析命令行参数
parser = argparse.ArgumentParser(description='绘制威科夫分析图')
parser.add_argument('input_csv', nargs='?', default="../ADAUSDC_4h_Cleaned.csv", help='输入的 CSV 文件路径')
args = parser.parse_args()

file_path = args.input_csv
if not os.path.exists(file_path):
    print(f"❌ 错误: 找不到文件 {file_path}")
    sys.exit(1)

# 生成输出文件名基础 (从输入文件名中提取)
# 例如: ../ADAUSDC_4h_Cleaned.csv -> ADAUSDC_4h
base_name = os.path.splitext(os.path.basename(file_path))[0].replace("_Cleaned", "")
print(f"📖 读取数据: {file_path}")
df = pd.read_csv(file_path)

# 转换时间索引
df['Date'] = pd.to_datetime(df['Human_Time'])
df.set_index('Date', inplace=True)

# 确保数值类型
cols = ['Open', 'High', 'Low', 'Close', 'Volume']
for c in cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# --- 3. 威科夫结构分析 (启发式/模拟) ---
# 注意：作为脚本，这里主要负责“绘图”，真正的智能分析应由LLM完成。
# 但为了演示效果，这里选取最近一段明显的行情进行标注。
# 假设我们关注最近的下跌趋势和潜在的恐慌抛售(SC)

# --- 3. 威科夫结构分析 (模拟 AI 分析结果) ---
# 目标：展示从 2025 年末的高点以来的下跌趋势，以及当前的吸筹结构
# 逻辑：
# 1. 2024年12月-2025年初: 潜在的派发顶部 (Buying Climax / UT)
# 2. 2026年1月: 恐慌抛售 (SC)

# 截取最近 1000 根 K 线 (约 5 个月) 以展示完整结构
# 4h 线：1000 根 ≈ 166 天，涵盖 2025年8月至今
plot_df = df.tail(1000).copy()

# A. 寻找区间内的最高点 (潜在的 BC/UT)
max_idx = plot_df['High'].idxmax()
bc_price = plot_df.loc[max_idx, 'High']

# B. 寻找区间内的最低点 (SC)
min_idx = plot_df['Low'].idxmin()
sc_price = plot_df.loc[min_idx, 'Low']

# C. 寻找 SC 后的 AR
after_sc = plot_df[plot_df.index > min_idx]
ar_price = sc_price * 1.15 # 默认
ar_idx = plot_df.index[-1]
if not after_sc.empty:
    ar_idx_real = after_sc['High'].idxmax()
    ar_price = after_sc.loc[ar_idx_real, 'High']
    tr_top = ar_price
    tr_bottom = sc_price
else:
    tr_top = ar_price
    tr_bottom = sc_price

# --- 4. 绘图 ---
msg = f"威科夫全景分析图 ({base_name.replace('_', ' ')})"
print(f"🎨 正在绘制: {msg}")

# 设置 mplfinance 风格
s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={
    'font.family': 'SimHei' if os.name == 'nt' else 'Arial Unicode MS',
    'font.size': 12
})

# 准备标注点
annotations = [
    (max_idx, bc_price, "BC/UT\n抢购高潮/上冲"),
    (min_idx, sc_price, "SC\n恐慌抛售"),
]
if not after_sc.empty:
    annotations.append((ar_idx_real, ar_price, "AR\n自动反弹"))

# 简单识别中间的 SOW (弱势信号): 高点下移过程中的显著长阴
# 这里简单取高点到低点中间某处的大阴线示意
mid_df = plot_df[(plot_df.index > max_idx) & (plot_df.index < min_idx)]
if not mid_df.empty:
    # 找跌幅最大的一根
    sow_idx = (mid_df['Close'] - mid_df['Open']).idxmin()
    sow_price = mid_df.loc[sow_idx, 'Low']
    annotations.append((sow_idx, sow_price, "SOW\n弱势信号"))

# 构造绘图
t_start = min_idx # TR 开始于 SC
t_end = plot_df.index[-1]

# 绘图配置
fig, axes = mpf.plot(
    plot_df,
    type='candle',
    volume=True,
    title=msg,
    style=s,
    returnfig=True,
    figsize=(24, 12), 
    panel_ratios=(6, 2),
    tight_layout=True, # 必须配合非紧缩 bbox
    
    # 绘制 TR (仅针对底部吸筹区)
    hlines=dict(hlines=[tr_top, tr_bottom], colors=['red', 'green'], linestyle='-.', linewidths=2),
    
    # 简单绘制下跌趋势线 (连接 BC 和 中间某个高点) 示意
    # alines=... (暂略，避免坐标转换复杂问题)
)

# 获取 ax 对象
ax_main = axes[0]

# 辅助函数：获取日期对应的整数坐标
def get_x_loc(timestamp):
    try:
        return plot_df.index.get_loc(timestamp)
    except KeyError:
        return 0

# 绘制吸筹区矩形 (半透明)
x_start_idx = get_x_loc(t_start)
x_end_idx = len(plot_df) - 1

rect = plt.Rectangle((x_start_idx, tr_bottom), x_end_idx - x_start_idx, tr_top - tr_bottom, 
                     facecolor='green', alpha=0.1, edgecolor='none')
ax_main.add_patch(rect)

# 添加文字标注
for date, price, label in annotations:
    # [修复] 将日期转换为对应的整数 X 坐标
    x_idx = get_x_loc(date)
    
    ax_main.annotate(
        label, 
        xy=(x_idx, price), 
        xytext=(x_idx, price * 0.95), # 文字在下方
        arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5),
        fontsize=14, # 加大字体
        color='red',
        fontproperties=font_prop,
        fontweight='bold',
        ha='center', # 水平居中
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8) # 增加背景框确保清晰
    )

# 标注 Trading Range (只在左侧 SC 处标注一次即可，或者在右侧延伸)
ax_main.text(x_start_idx, tr_top, f"TR 上沿: {tr_top:.4f}", color='red', fontsize=12, ha='right', va='bottom', fontproperties=font_prop)
ax_main.text(x_start_idx, tr_bottom, f"TR 下沿: {tr_bottom:.4f}", color='green', fontsize=12, ha='right', va='top', fontproperties=font_prop)

# [新增] 打印分析数据供 AI 生成报告
print("\n=== AI 分析数据源 ===")
print(f"TR 上沿 (AR): {tr_top:.4f}")
print(f"TR 下沿 (SC): {tr_bottom:.4f}")
print(f"SC 日期: {t_start}")
print(f"当前价格: {plot_df['Close'].iloc[-1]:.4f}")
print("=====================\n")

# 保存 (动态文件名)
output_file = f"{base_name}_Wyckoff_Chart.png"
# 移除 bbox_inches='tight'，因为它可能导致尺寸计算异常
# 设置固定的 dpi=150，配合 figsize=(24, 12)，输出图片宽度约为 3600px，足够清晰且不会过大
plt.savefig(output_file, dpi=150) 
print(f"💾 图片已保存: {output_file}")
