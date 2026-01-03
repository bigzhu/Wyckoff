import requests
import pandas as pd
import time
from datetime import datetime, timedelta

import argparse
import sys

# ================= 配置区 =================
def get_config():
    default_symbol = "ADAUSDC"
    default_interval = "4h"
    
    parser = argparse.ArgumentParser(description='Binance K线数据获取工具 (使用 Data API)')
    parser.add_argument('symbol', nargs='?', default=default_symbol, help=f'交易对 (默认: {default_symbol})')
    parser.add_argument('interval', nargs='?', default=default_interval, help=f'时间周期 (默认: {default_interval})')
    # [新增] 支持 --days 参数
    parser.add_argument('--days', type=int, default=0, help='从最近 N 天前开始拉取 (默认 0 表示从 2024-01-01 开始)')
    
    args = parser.parse_args()
    
    symbol = args.symbol.upper()
    interval = args.interval.lower()
    
    # 计算起始时间
    if args.days > 0:
        start_date = datetime.now() - timedelta(days=args.days)
        start_ts = int(start_date.timestamp() * 1000)
    else:
        # 默认 2024-01-01
        start_ts = int(datetime(2024, 1, 1).timestamp() * 1000)
    
    print(f"✅ 已确认: {symbol} | {interval} | 起始时间: {datetime.fromtimestamp(start_ts/1000)}")
    return symbol, interval, start_ts

SYMBOL, INTERVAL, START_TIME = get_config()

# 使用 data-api.binance.vision 替代 api.binance.com 以绕过地区限制
BASE_URL = "https://data-api.binance.vision/api/v3/klines"

COLUMNS = [
    "Open_time", "Open", "High", "Low", "Close", "Volume",
    "Close_time", "Quote_asset_volume", "Number_of_trades",
    "Taker_buy_base_asset_volume", "Taker_buy_quote_asset_volume", "Ignore"
]

def fetch_all_data(symbol, interval, start_ts):
    """
    通过 Binance API 分页拉取所有历史数据直到最新
    """
    all_data = []
    current_start = start_ts
    
    print(f"🚀 开始从 API 拉取数据 (起始: {datetime.fromtimestamp(start_ts/1000)}) ...")
    
    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "limit": 1000  # API 最大限制
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            if response.status_code != 200:
                print(f"❌ API 请求失败: {response.text}")
                break
            
            data = response.json()
            if not data:
                print("⚠️ 没有更多数据了。")
                break
                
            all_data.extend(data)
            
            # 打印进度
            last_ts = data[-1][0]
            last_date = datetime.fromtimestamp(last_ts/1000)
            print(f"\r📥 已拉取至: {last_date} (总 K 线数: {len(all_data)})", end="", flush=True)
            
            # 更新下一次请求的起始时间 (最后一根 K 线开盘时间 + 1ms 防止重复? 或者直接取 Close_time + 1? )
            # 实际上取最后一根 Open_time + 1ms 依然会包含这根还是？Binance API 文档建议 startTime。
            # 简单做法：取最后一根的 close_time + 1
            current_start = data[-1][6] + 1
            
            # 如果拉取数量少于 Limit，说明已经是最新的了
            if len(data) < 1000:
                print("\n✅ 数据拉取完毕。")
                break
                
            # 稍微休眠防止触发极端频控 (虽然后台限制是 1200权重/分，单次 K 线权重仅为 2)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"\n❌ 网络或解析错误: {e}")
            break
            
    return all_data

def main():
    raw_data = fetch_all_data(SYMBOL, INTERVAL, START_TIME)
    
    if not raw_data:
        print("❌ 未获取到任何数据")
        return

    print("\n🧹 正在清洗数据...")
    df = pd.DataFrame(raw_data, columns=COLUMNS)
    
    # --- 数据清洗与格式化 ---
    
    # 1. 类型转换
    numeric_cols = ["Open", "High", "Low", "Close", "Volume", "Open_time"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 2. 增加人类可读时间 (UTC+8)
    df['Human_Time'] = pd.to_datetime(df['Open_time'], unit='ms') + timedelta(hours=8)
    
    # 3. 整理列顺序
    final_cols = ['Human_Time', 'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                  'Close_time', 'Quote_asset_volume', 'Number_of_trades', 
                  'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore']
    df = df[final_cols]
    
    # 4. 保存
    output_name = f"{SYMBOL}_{INTERVAL}_Cleaned.csv"
    df.to_csv(output_name, index=False)
    
    print(f"✅ 成功保存: {output_name}")
    print(f"📊 数据范围: {df['Human_Time'].iloc[0]} 至 {df['Human_Time'].iloc[-1]}")
    print(f"📈 总行数: {len(df)}")

if __name__ == "__main__":
    main()