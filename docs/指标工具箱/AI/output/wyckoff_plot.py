
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
import argparse
import sys

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

# --- 2. 参数解析 & 数据读取 ---
parser = argparse.ArgumentParser(description='绘制威科夫分析图 (Master Mode)')
parser.add_argument('input_csv', nargs='?', default="../ADAUSDC_4h_Cleaned.csv", help='输入的 CSV 文件路径')
args = parser.parse_args()

file_path = args.input_csv
if not os.path.exists(file_path):
    print(f"❌ 错误: 找不到文件 {file_path}")
    sys.exit(1)

base_name = os.path.splitext(os.path.basename(file_path))[0].replace("_Cleaned", "")
print(f"📖 读取数据: {file_path}")
df = pd.read_csv(file_path)

df['Date'] = pd.to_datetime(df['Human_Time'])
df.set_index('Date', inplace=True)

for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# --- 3. 结构分析 (优化后的启发式逻辑) ---
# 截取最近 400 根 K 线以获得更清晰的视觉重点
plot_df = df.tail(400).copy()

# A. 趋势顶点 (BC/UTAD)
max_idx = plot_df['High'].idxmax()
bc_price = plot_df.loc[max_idx, 'High']

# B. 趋势底点 (SC/Spring)
min_idx = plot_df['Low'].idxmin()
sc_price = plot_df.loc[min_idx, 'Low']

# C. TR 范围预测
after_sc = plot_df[plot_df.index > min_idx]
if not after_sc.empty:
    ar_idx_real = after_sc['High'].idxmax()
    tr_top = after_sc.loc[ar_idx_real, 'High']
    tr_bottom = sc_price
else:
    tr_top = bc_price * 0.98
    tr_bottom = sc_price
    ar_idx_real = plot_df.index[-1]

# --- 4. 绘图 (Master Level 暗色风格) ---
print(f"🎨 正在绘制 Master 风格全景图...")

# 定义专业颜色
COLOR_TR_BOX = '#263238' # 深蓝灰背景
COLOR_GOLD = '#FFD700'   # 金色 (上沿)
COLOR_AZURE = '#00BFFF'  # 天蓝色 (下沿)
COLOR_TEXT = '#FFFFFF'
COLOR_GRID = '#37474F'

# 自定义 mplfinance 风格 (基于 nightclouds 但更极致)
s = mpf.make_mpf_style(
    base_mpf_style='nightclouds',
    gridcolor=COLOR_GRID,
    facecolor='#121212', # 纯黑背景
    edgecolor='#333333',
    figcolor='#121212',
    y_on_right=True,
    marketcolors=mpf.make_marketcolors(
        up='#00c853', down='#ff5252',
        inherit=True
    )
)

# 标注列表 (时间, 价格, 标签, 偏移方向, 颜色)
# 偏移方向: 1 为上方, -1 为下方
annotations = [
    (max_idx, bc_price, "BC/UTAD", 1, COLOR_GOLD),
    (min_idx, sc_price, "SC/SPRING", -1, COLOR_AZURE),
]
if not after_sc.empty:
    annotations.append((ar_idx_real, tr_top, "AR/LPSY", 1, COLOR_TEXT))

# 绘图调用
fig, axes = mpf.plot(
    plot_df,
    type='candle',
    volume=True,
    title=f"\nWYCKOFF MASTER ANALYSIS: {base_name.replace('_', ' ')}",
    style=s,
    returnfig=True,
    figsize=(20, 10),
    panel_ratios=(1, 0.3),
    tight_layout=True,
    hlines=dict(hlines=[tr_top, tr_bottom], colors=[COLOR_GOLD, COLOR_AZURE], linestyle='--', linewidths=1.5, alpha=0.6)
)

ax_main = axes[0]
ax_vol = axes[2]

# --- 5. 装饰图表 ---

# 1. 绘制 TR 阴影背景
def get_x_loc(timestamp):
    try: return plot_df.index.get_loc(timestamp)
    except: return 0

x_start = get_x_loc(min_idx)
x_end = len(plot_df) - 1
rect = plt.Rectangle((x_start, tr_bottom), x_end - x_start, tr_top - tr_bottom, 
                     facecolor='#FFD700', alpha=0.08, edgecolor='none', zorder=0)
ax_main.add_patch(rect)

# 2. 绘制智能文字标注
for date, price, label, direction, color in annotations:
    x_idx = get_x_loc(date)
    offset = (plot_df['High'].max() - plot_df['Low'].min()) * 0.05 * direction
    
    ax_main.annotate(
        label,
        xy=(x_idx, price),
        xytext=(x_idx, price + offset),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.2, alpha=0.8),
        fontsize=11,
        color=color,
        fontweight='bold',
        ha='center',
        va='bottom' if direction > 0 else 'top',
        bbox=dict(boxstyle="round,pad=0.2", fc="#1A1A1A", ec=color, alpha=0.9, lw=1)
    )

# 3. 添加左上角数据盒 (Master Box)
info_text = (
    f"SYMBOL: {base_name.split('_')[0]}\n"
    f"INTERVAL: {base_name.split('_')[1]}\n"
    f"CURRENT: {plot_df['Close'].iloc[-1]:.4f}\n"
    f"TR TOP: {tr_top:.4f}\n"
    f"TR BOT: {tr_bottom:.4f}"
)
props = dict(boxstyle='round', facecolor='#1A1A1A', alpha=0.8, edgecolor=COLOR_GOLD, lw=1.5)
ax_main.text(0.02, 0.95, info_text, transform=ax_main.transAxes, fontsize=12,
             verticalalignment='top', bbox=props, color=COLOR_TEXT, fontfamily='monospace')

# 4. 优化坐标轴
ax_main.yaxis.set_label_position("right")
ax_main.tick_params(colors=COLOR_TEXT, which='both')
for spine in ax_main.spines.values():
    spine.set_edgecolor(COLOR_GRID)

# --- 6. 导出图片 & 报告 ---
output_file = f"{base_name}_Wyckoff_Chart.png"
plt.savefig(output_file, dpi=120, facecolor='#121212')
print(f"💾 图片已保存: {output_file}")

# 打印数据供 AI 参考
print("\n=== AI 分析数据源 ===")
print(f"TR 上沿 (AR): {tr_top:.4f}")
print(f"TR 下沿 (SC): {tr_bottom:.4f}")
print(f"SC 日期: {min_idx}")
print(f"当前价格: {plot_df['Close'].iloc[-1]:.4f}")
print("=====================\n")

# 生成 Markdown 报告内容
md_output_file = f"{base_name}_Wyckoff_Analysis.md"
current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
analysis_template = f"""# 威科夫深度研报: {base_name.replace("_", " ")}

**分析日期**: {current_date}
**数据范围**: {plot_df.index[0].strftime("%Y-%m-%d")} -> {plot_df.index[-1].strftime("%Y-%m-%d %H:%M")}

---

## 1. 威科夫全景透视图 (Master View)

![Wyckoff Chart](./{os.path.basename(output_file)})

---

## 2. 核心量价数据

| 指标 | 数值 | 威科夫含义 |
| :--- | :--- | :--- |
| **TR 上沿 (Resistance)** | **{tr_top:.4f}** | 供应释放区 (AR/LPSY) |
| **TR 下沿 (Support)** | **{tr_bottom:.4f}** | 需求介入区 (SC/Spring) |
| **当前价格 (Closing)** | **{plot_df['Close'].iloc[-1]:.4f}** | {'区间震荡中' if tr_bottom <= plot_df['Close'].iloc[-1] <= tr_top else '寻求趋势突破'} |

---

## 3. 结构化简述

1. **结构形态**: 价格目前处于由 {tr_bottom:.4f} 与 {tr_top:.4f} 构成的交易区间 (Trading Range) 内。
2. **量价特征**: 识别到关键的 {'恐慌抛售 (SC)' if min_idx in plot_df.index else '震荡低点'}。
3. **主点位参考**: 
   - **防御位**: {tr_bottom:.4f} (若持续放量跌破，标志着派发完成)。
   - **进攻位**: {tr_top:.4f} (若缩量回踩不破，标志着吸筹完成)。

---
> *本报告由智能分析系统生成。威科夫法则提示：在结果显现之前，请耐心等待供求平衡的打破。*
"""

with open(md_output_file, "w", encoding="utf-8") as f:
    f.write(analysis_template)

print(f"📝 报告已更新: {md_output_file}")
