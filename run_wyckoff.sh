#!/bin/bash

# run_wyckoff.sh
# 自动化执行威科夫分析流程: 获取数据 -> 清洗 -> 绘图 -> 生成报告

# 默认参数
SYMBOL="ADAUSDC"
INTERVAL="4h"
DAYS=0
HISTORY=400

# 解析参数
if [ "$1" ]; then SYMBOL=$1; fi
if [ "$2" ]; then INTERVAL=$2; fi
if [ "$3" ]; then DAYS=$3; fi
if [ "$4" ]; then HISTORY=$4; fi

echo "🚀 开始执行自动化分析流程..."
echo "📊 交易对: $SYMBOL | 周期: $INTERVAL | 范围: ${DAYS}天 (0=全部) | AI 历史: ${HISTORY}条"

# 1. 获取数据 (使用 binance_data_pro.py)
echo "----------------------------------------"
echo "📥 步骤 1: 获取并清洗数据..."
# 根据是否有 days 参数构建命令
if [ "$DAYS" -gt 0 ]; then
    python3 docs/指标工具箱/AI/binance_data_pro.py $SYMBOL $INTERVAL --days $DAYS
else
    python3 docs/指标工具箱/AI/binance_data_pro.py $SYMBOL $INTERVAL
fi

if [ $? -ne 0 ]; then
    echo "❌ 数据获取失败，流程终止。"
    exit 1
fi

# 定义文件名
CSV_FILE="${SYMBOL}_${INTERVAL}_Cleaned.csv"
TARGET_DIR="docs/指标工具箱/AI"
OUTPUT_DIR="docs/指标工具箱/AI/output"

# 2. 移动数据文件
echo "----------------------------------------"
echo "🚚 步骤 2: 归档数据文件..."
if [ -f "$CSV_FILE" ]; then
    mv "$CSV_FILE" "$TARGET_DIR/"
    echo "✅ 已移动 $CSV_FILE -> $TARGET_DIR/"
else
    echo "❌ 找不到生成的 CSV 文件: $CSV_FILE"
    exit 1
fi

# 3. 执行分析 (绘图 + 报告)
echo "----------------------------------------"
echo "🎨 步骤 3: 执行威科夫分析 (绘图 & 报告)..."
# 切换到 output 目录执行，方便生成的文件直接在该目录下
cd "$OUTPUT_DIR" || exit

# 运行绘图脚本 (注意传入相对路径 ../$CSV_FILE)
# 需要设置 PYTHONPATH 以防模块导入问题 (虽然脚本比较独立)
export PYTHONPATH=$PYTHONPATH:$(python3 -m site --user-site)
python3 wyckoff_plot.py "../$CSV_FILE"

if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "✅ 自动化分析流程完成！"
    echo "📄 查看报告: $OUTPUT_DIR/${SYMBOL}_${INTERVAL}_Wyckoff_Analysis.md"
    echo "🖼️ 查看图表: $OUTPUT_DIR/${SYMBOL}_${INTERVAL}_Wyckoff_Chart.png"
    
    # 4. 执行 AI 深度分析 (如果配置了 API)
    # 检查项目根目录下的 .env 是否存在且有 KEY
    # 当前目录是 docs/指标工具箱/AI/output, 根目录是 ../../../..
    ROOT_ENV="../../../../.env"
    
    if [ -f "$ROOT_ENV" ] && grep -q "GOOGLE_API_KEY" "$ROOT_ENV"; then
        echo "----------------------------------------"
        echo "🧠 步骤 4: 调用 Gemini AI 生成深度分析报告..."
        # 回到项目根目录执行，因为 ai_analyze.py 内部逻辑依赖相对路径找 .env
        cd ../../../.. || exit
        
        python3 docs/指标工具箱/AI/ai_analyze.py "$TARGET_DIR/$CSV_FILE" --history $HISTORY
        
        if [ $? -eq 0 ]; then
            echo "✅ AI 分析完成！报告已更新。"
        else
            echo "⚠️ AI 分析失败，保留模板报告。"
        fi
    else
        echo "----------------------------------------"
        echo "ℹ️ 未检测到 GOOGLE_API_KEY，跳过 AI 深度分析 (保留模板报告)。"
    fi

else
    echo "❌ 分析脚本执行失败。"
    exit 1
fi
