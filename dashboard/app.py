import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 核心计算函数 ---
def calculate_buzz_score(row, vol_weight, sent_weight):
    # 简单的加权算法，后续你可以根据需求在这里调整公式
    score = (row['mentions_growth'] * vol_weight) + (row['sentiment_avg'] * sent_weight)
    return round(score, 2)

# --- 页面配置 ---
st.set_page_config(page_title="Stock Buzz Dashboard", layout="wide")
st.title("📈 Stock Mentions & Market Correlation")

# --- 侧边栏：参数调整 ---
st.sidebar.header("控制面板")
ticker = st.sidebar.text_input("股票代码", "NVDA").upper()
vol_w = st.sidebar.slider("提及量权重", 0.0, 1.0, 0.6)
sent_w = st.sidebar.slider("情绪权重", 0.0, 1.0, 0.4)

# --- 读取 GitHub Action 采集的数据 ---
try:
    # 确保读取时处理好类型
    df = pd.read_csv('data/history.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = df['price'].astype(float)
    df['buzz_score'] = df.apply(lambda r: calculate_buzz_score(r, vol_w, sent_w), axis=1)
    
    # --- 顶层指标展示 ---
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Buzz Score", last_row['buzz_score'], round(last_row['buzz_score'] - prev_row['buzz_score'], 2))
    col2.metric("实时股价 ($)", f"{last_row['price']}", round(last_row['price'] - prev_row['price'], 2))
    col3.metric("提及量 (24h)", int(last_row['mentions']))

    # --- 双轴可视化图表 ---
    st.subheader(f"{ticker} 情绪 vs 价格走势")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. 绘制 Buzz Score (主坐标轴 - 左)
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['buzz_score'], name="Buzz Score (情绪热度)", 
                   line=dict(color='#00FFCC', width=3)),
        secondary_y=False,
    )
    
    # 2. 绘制 股价 (次坐标轴 - 右)
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['price'], name="Stock Price (股价)", 
                   line=dict(color='#FF3399', dash='dot')),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 数据表格 ---
    with st.expander("查看原始历史数据"):
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

except Exception as e:
    st.warning(f"等待数据初始化中... 如果这是第一次部署，请先运行一次 GitHub Action。")
    st.info(f"技术细节提示: {e}")
