import requests
import datetime
import csv

TICKERS = ["NVDA","AAPL","TSLA"]

NEWS_API = "YOUR_NEWSAPI_KEY"

today = datetime.date.today()

results = []

for ticker in TICKERS:

    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API}"

    r = requests.get(url).json()

    mentions = len(r.get("articles", []))

    results.append({
        "date": today,
        "ticker": ticker,
        "news_mentions": mentions
    })

file = "data/mentions.csv"

with open(file,"a",newline="") as f:

    writer = csv.DictWriter(f,fieldnames=["date","ticker","news_mentions"])

    for row in results:
        writer.writerow(row)
