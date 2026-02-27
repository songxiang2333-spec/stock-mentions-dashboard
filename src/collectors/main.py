import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os

def collect_daily_data(ticker="NVDA"):
    # 1. 获取真实股价 (代替 Alpha Vantage)
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    current_price = hist['Close'].iloc[-1] if not hist.empty else 0

    # 2. 模拟社交提及和情绪 (因为你还没有 NewsAPI Key)
    # 我们模拟：提及数在 500-1500 之间波动，情绪在 -0.2 到 0.8 之间
    mock_mentions = np.random.randint(500, 1500)
    mock_sentiment = np.round(np.random.uniform(-0.2, 0.8), 2)
    mock_growth = np.round(np.random.uniform(0.8, 1.5), 2)

    new_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ticker': ticker,
        'price': round(current_price, 2),
        'mentions': mock_mentions,
        'sentiment_avg': mock_sentiment,
        'mentions_growth': mock_growth
    }

    # 3. 写入 CSV
    file_path = 'data/history.csv'
    
    # 确保文件夹存在
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # 如果今天的数据已存在，则更新；否则追加
        if new_data['date'] in df['date'].values:
            df.loc[df['date'] == new_data['date'], :] = list(new_data.values())
        else:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])
    
    df.to_csv(file_path, index=False)
    print(f"✅ 数据已更新: {new_data}")

if __name__ == "__main__":
    collect_daily_data()
