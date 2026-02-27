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

   # ... 之前的代码保持不变 ...

    new_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ticker': ticker,
        'price': float(current_price),  # 强制转为浮点数
        'mentions': int(mock_mentions),
        'sentiment_avg': float(mock_sentiment),
        'mentions_growth': float(mock_growth)
    }

    file_path = 'data/history.csv'
    os.makedirs('data', exist_ok=True)
    
    if os.path.exists(file_path):
        # 读取时强制指定 price 这一列为 float，避免 Pandas 误判
        df = pd.read_csv(file_path)
        
        # 将新数据转为 DataFrame
        new_df = pd.DataFrame([new_data])
        
        # 统一两个 DataFrame 的类型，防止合并时报错
        df['price'] = df['price'].astype(float)
        
        if new_data['date'] in df['date'].values:
            df.loc[df['date'] == new_data['date'], :] = list(new_data.values())
        else:
            df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])
    
    # 保存
    df.to_csv(file_path, index=False)
