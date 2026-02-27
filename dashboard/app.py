import streamlit as st
import pandas as pd
import plotly.express as px
from vadersentiment.vaderSentiment import SentimentIntensityAnalyzer

# 初始化情绪分析器
analyzer = SentimentIntensityAnalyzer()

def calculate_buzz_score(row, vol_weight, sent_weight):
    """
    Buzz Score 计算逻辑:
    Score = (归一化体积 * vol_weight) + (情绪正负面 * sent_weight)
    """
    # 模拟简单的 Buzz 逻辑：提及量 * 权重 + 情绪分 * 权重
    score = (row['mentions_growth'] * vol_weight) + (row['sentiment_avg'] * sent_weight)
    return round(score, 2)

# --- 页面配置 ---
st.set_page_config(page_title="Stock Buzz Dashboard", layout="wide")
st.title("📈 Stock Mentions & Trend Analysis")

# --- 侧边栏：参数调整 ---
st.sidebar.header("核心参数微调")
ticker = st.sidebar.text_input("输入股票代码", "NVDA").upper()

st.sidebar.subheader("Buzz Score 权重设置")
vol_w = st.sidebar.slider("提及量增长权重", 0.0, 1.0, 0.6)
sent_w = st.sidebar.slider("情绪正向权重", 0.0, 1.0, 0.4)

# --- 数据模拟 (后续对接你的 Data Pipeline) ---
# 假设这是你每日采集保存到 data/history.csv 的数据
data = {
    'date': pd.date_range(start='2026-02-01', periods=10),
    'mentions': [120, 150, 300, 280, 450, 600, 550, 800, 950, 1100],
    'sentiment_avg': [0.1, 0.2, 0.4, 0.3, 0.5, 0.6, 0.4, 0.7, 0.8, 0.9],
    'mentions_growth': [1.0, 1.2, 2.0, 0.9, 1.6, 1.3, 0.9, 1.4, 1.2, 1.1]
}
df = pd.DataFrame(data)

# 计算实时 Buzz Score
df['buzz_score'] = df.apply(lambda r: calculate_buzz_score(r, vol_w, sent_w), axis=1)

# --- 仪表板展示 ---
col1, col2, col3 = st.columns(3)
with col1:
    current_buzz = df['buzz_score'].iloc[-1]
    st.metric("Current Buzz Score", current_buzz, delta=round(current_buzz - df['buzz_score'].iloc[-2], 2))
with col2:
    st.metric("Avg Sentiment", f"{df['sentiment_avg'].iloc[-1]*100:.1f}%")
with col3:
    st.metric("Total Mentions (24h)", df['mentions'].iloc[-1])

# --- 图表分析 ---
st.subheader(f"{ticker} 趋势分析")
fig = px.line(df, x='date', y=['buzz_score', 'sentiment_avg'], 
              title="Buzz Score vs Sentiment Over Time",
              labels={"value": "Score", "date": "Date"})
st.plotly_chart(fig, use_container_width=True)

# --- 数据导出 ---
st.subheader("数据导出")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("下载分析报表 (CSV)", data=csv, file_name=f"{ticker}_buzz_report.csv")
