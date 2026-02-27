import os
import pandas as pd
import yfinance as yf
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import time

# 初始化情绪分析器
analyzer = SentimentIntensityAnalyzer()

def get_sentiment_score(ticker, api_key):
    """抓取新闻并使用 VADER 计算平均情绪分"""
    if not api_key:
        return 0.5  # 无 Key 时返回中性分
    
    url = f"https://newsapi.org/v2/everything?q={ticker}&language=en&sortBy=publishedAt&pageSize=10&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            return 0.5
        
        scores = []
        for art in articles:
            text = f"{art.get('title', '')} {art.get('description', '')}"
            # VADER 评分：compound 分值范围是 [-1, 1]
            vs = analyzer.polarity_scores(text)
            scores.append(vs['compound'])
        
        # 将 [-1, 1] 映射到 [0, 1] 方便展示：(score + 1) / 2
        avg_score = sum(scores) / len(scores)
        normalized_score = round((avg_score + 1) / 2, 2)
        return normalized_score
    except Exception as e:
        print(f"新闻抓取失败 ({ticker}): {e}")
        return 0.5

def collect_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    history_path = os.path.join(base_dir, 'data', 'history.csv')
    target_path = os.path.join(base_dir, 'data', 'targets.csv')
    api_key = os.environ.get('NEWS_API_KEY')

    # --- 核心改动：读取目标列表 ---
    if os.path.exists(target_path):
        target_df = pd.read_csv(target_path)
        tickers = target_df['Ticker'].tolist()
    else:
        tickers = ["NVDA", "META", "AAPL"] # 默认值

    all_new_data = []
    # ... 剩下的循环抓取逻辑保持不变 ...

    for ticker in tickers:
        print(f"正在处理: {ticker}...")
        
        # 1. 获取股价
        stock = yf.Ticker(ticker)
        price = stock.fast_info['last_price']
        
        # 2. 获取真实情绪分 (NewsAPI + VADER)
        sentiment = get_sentiment_score(ticker, api_key)
        
        # 3. 模拟提及量增长 (后续可接入 Reddit API)
        # 这里我们暂用随机数，但情绪已经是真实的了
        mentions = 1000 + (sentiment * 500) 
        growth = round(1.0 + (sentiment - 0.5), 2)

        all_new_data.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'ticker': ticker,
            'price': round(price, 2),
            'mentions': int(mentions),
            'sentiment_avg': sentiment,
            'mentions_growth': growth
        })
        time.sleep(1) # 避免请求过快

 # ... 前面的抓取逻辑 ...
    
    # 4. 保存到 CSV (修复变量名错误)
    new_df = pd.DataFrame(all_new_data)
    
    # 这里的变量名必须和你前面定义的 history_path 保持一致
    if os.path.exists(history_path): 
        df = pd.read_csv(history_path)
        # 合并并去重
        df = pd.concat([df, new_df]).drop_duplicates(subset=['date', 'ticker'], keep='last')
    else:
        df = new_df
    
    # 同样，这里也改为 history_path
    df.to_csv(history_path, index=False)
    print(f"✅ 成功更新了 {len(tickers)} 只股票的数据")

if __name__ == "__main__":
    collect_data()
