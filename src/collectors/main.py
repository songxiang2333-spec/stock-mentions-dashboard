import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import random

def collect_stock_data(ticker="NVDA"):
    # 1. 自动定位路径（绝对路径确保 GitHub Action 写入成功）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    data_dir = os.path.join(base_dir, 'data')
    file_path = os.path.join(data_dir, 'history.csv')
    
    # 确保 data 文件夹存在
    os.makedirs(data_dir, exist_ok=True)

    print(f"开始采集 {ticker} 数据...")
    print(f"目标文件路径: {file_path}")

    # 2. 获取真实股价 (yfinance)
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.fast_info['last_price']
    except Exception as e:
        print(f"获取股价失败: {e}，使用模拟价格")
        current_price = 185.0

    # 3. 模拟社交媒体数据 (后续可接入 Reddit/News API)
    # 这里的逻辑是：生成一些随机波动，方便你在图表上看到效果
    mock_mentions = random.randint(800, 1500)
    mock_sentiment = round(random.uniform(0.4, 0.8), 2)
    mock_growth = round(random.uniform(0.9, 1.3), 2)

    # 4. 构建新数据行
    new_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ticker': ticker,
        'price': float(current_price),
        'mentions': int(mock_mentions),
        'sentiment_avg': float(mock_sentiment),
        'mentions_growth': float(mock_growth)
    }
    new_df = pd.DataFrame([new_data])

    # 5. 读取并更新 CSV
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            df = pd.read_csv(file_path)
            # 确保类型统一，防止 TypeError
            df['price'] = df['price'].astype(float)
            
            # 如果日期已存在，则更新；否则追加
            if new_data['date'] in df['date'].astype(str).values:
                df.loc[df['date'].astype(str) == new_data['date'], :] = list(new_data.values())
                print(f"更新了 {new_data['date']} 的现有记录")
            else:
                df = pd.concat([df, new_df], ignore_index=True)
                print("追加了新的一行数据")
        except Exception as e:
            print(f"读取 CSV 出错: {e}，将重新创建文件")
            df = new_df
    else:
        print("CSV 不存在或为空，正在初始化...")
        df = new_df

    # 6. 保存并强制写入
    df.to_csv(file_path, index=False)
    print("✅ 数据已成功保存到 CSV 文件")
    
    # 调试：打印最后 3 行内容到日志中
    print("最新数据概览:")
    print(df.tail(3))

if __name__ == "__main__":
    collect_stock_data()
