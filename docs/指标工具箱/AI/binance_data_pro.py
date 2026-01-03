import requests
import zipfile
import io
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= 配置区 =================
SYMBOL = "ADAUSDC"
INTERVAL = "1d"
START_DATE = datetime(2024, 1, 1) 
END_DATE = datetime.now() - timedelta(days=1)
MAX_WORKERS = 20
CACHE_DIR = "binance_data_cache"

BASE_URL = f"https://data.binance.vision/data/spot/daily/klines/{SYMBOL}/{INTERVAL}"
COLUMNS = [
    "Open_time", "Open", "High", "Low", "Close", "Volume",
    "Close_time", "Quote_asset_volume", "Number_of_trades",
    "Taker_buy_base_asset_volume", "Taker_buy_quote_asset_volume", "Ignore"
]
# ==========================================

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_data_for_day(date_str):
    file_name = f"{SYMBOL}-{INTERVAL}-{date_str}.zip"
    local_path = os.path.join(CACHE_DIR, file_name)
    
    # 1. 尝试本地加载
    if os.path.exists(local_path):
        try:
            with zipfile.ZipFile(local_path) as z:
                with z.open(z.namelist()[0]) as f:
                    # on_bad_lines='skip' 防止某行数据列数不对
                    df = pd.read_csv(f, header=None, names=COLUMNS, dtype=str, on_bad_lines='skip')
                    return df, "Local"
        except:
            pass 

    # 2. 本地不存在则下载
    url = f"{BASE_URL}/{file_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(local_path, 'wb') as f_out:
                f_out.write(response.content)
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                with z.open(z.namelist()[0]) as f:
                    return pd.read_csv(f, header=None, names=COLUMNS, dtype=str, on_bad_lines='skip'), "Download"
        return None, "Missing"
    except:
        return None, "Error"

def main():
    date_list = [ (START_DATE + timedelta(days=i)).strftime("%Y-%m-%d") 
                 for i in range((END_DATE - START_DATE).days + 1) ]

    all_dfs = []
    print(f"🚀 启动 | 合并处理中...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_date = {executor.submit(get_data_for_day, d): d for d in date_list}
        for i, future in enumerate(as_completed(future_to_date), 1):
            df, source = future.result()
            if df is not None: all_dfs.append(df)
            print(f"\r进度: [{i}/{len(date_list)}] 处理源: {source:<10}", end="", flush=True)

    if not all_dfs:
        print("\n❌ 未能获取数据。")
        return

    print("\n📥 正在执行深度数据清洗...")
    final_df = pd.concat(all_dfs, ignore_index=True)

    # --- 关键清洗步骤 ---
    # 1. 转换为数字，非法字符变 NaN
    final_df['Open_time'] = pd.to_numeric(final_df['Open_time'], errors='coerce')
    
    # 2. 核心：过滤掉异常的时间戳数值
    # 正常 2024-2026 年的毫秒时间戳应该在 1.7e12 到 1.8e12 之间
    # 我们设定一个合理的阈值：1,500,000,000,000 到 2,000,000,000,000
    valid_mask = (final_df['Open_time'] > 1500000000000) & (final_df['Open_time'] < 2000000000000)
    final_df = final_df[valid_mask].copy()
    
    # 3. 排序
    final_df = final_df.sort_values('Open_time').drop_duplicates(subset=['Open_time'])

    # 4. 安全转换日期
    try:
        # unit='ms' 配合已经过滤过的数值，绝不会再报 OutOfBounds
        final_df['Human_Time'] = pd.to_datetime(final_df['Open_time'], unit='ms') + timedelta(hours=8)
        
        # 转换价格列为浮点数，方便后续分析
        price_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in price_cols:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        # 整理列顺序
        cols = ['Human_Time'] + [c for c in final_df.columns if c != 'Human_Time']
        final_df = final_df[cols]
    except Exception as e:
        print(f"\n⚠️ 日期转换警告 (已跳过转换): {e}")

    output_name = f"{SYMBOL}_{INTERVAL}_Cleaned.csv"
    final_df.to_csv(output_name, index=False)
    print(f"\n✅ 成功！数据已清洗。")
    print(f"📊 最终行数: {len(final_df)} | 文件: {output_name}")

if __name__ == "__main__":
    main()