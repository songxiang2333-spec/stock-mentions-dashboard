import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="AI Multi-Stock Intelligence", layout="wide", page_icon="🤖")

# --- 核心计算逻辑 ---
def calculate_buzz_score(row, vol_weight, sent_weight):
    # 归一化处理：情绪在 [0,1] 之间，0.5为中性
    # Buzz Score = 增长率 * 权重 + (情绪偏差 * 权重)
    sentiment_bias = row['sentiment_avg'] - 0.5
    score = (row['mentions_growth'] * vol_weight) + (sentiment_bias * sent_weight)
    return round(score, 2)

# --- 侧边栏：监控中心 ---
st.sidebar.title("🛠 控制面板")

# 1. Excel/CSV 上传入口 (你的需求 #2)
st.sidebar.subheader("上传监控清单")
uploaded_file = st.sidebar.file_uploader("导入 Excel (需包含 Ticker 列)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            upload_df = pd.read_excel(uploaded_file)
        else:
            upload_df = pd.read_csv(uploaded_file)
        
        if 'Ticker' in upload_df.columns:
            tickers = upload_df['Ticker'].dropna().unique().tolist()
            # 注意：Render 环境下文件写入是暂时的，通常用于即时展示
            # 这里我们可以展示即将监控的列表
            st.sidebar.success(f"已识别 {len(tickers)} 只股票！")
            st.sidebar.write(", ".join(tickers))
            st.sidebar.warning("💡 请将此清单同步至 GitHub 的 data/targets.csv 以持久化监控。")
        else:
            st.sidebar.error("错误：文件中未找到 'Ticker' 列")
    except Exception as e:
        st.sidebar.error(f"解析失败: {e}")

st.sidebar.markdown("---")

# 2. 算法权重设定 (你的需求 #5)
st.sidebar.subheader("Buzz 算法权重")
vol_w = st.sidebar.slider("提及增长权重", 0.0, 1.0, 0.7)
sent_w = st.sidebar.slider("情绪偏差权重", 0.0, 1.0, 0.3)

# 3. 报警设定入口 (你的需求 #4)
st.sidebar.subheader("🔔 动态提醒设定")
alert_threshold = st.sidebar.number_input("Buzz Score 报警阈值", value=1.2, step=0.1)
alert_email = st.sidebar.text_input("接收邮箱", placeholder="example@163.com")
if st.sidebar.button("保存报警设定"):
    # 这里未来可以接入 API 写入 config.json
    st.sidebar.toast("设定已记录（需同步至 GitHub 生效）")

# --- 主界面：数据展示 ---
st.title("📈 AI 股票热度与情绪监控系统")

# 加载历史数据
file_path = 'data/history.csv'
if os.path.exists(file_path):
    all_df = pd.read_csv(file_path)
    all_df['date'] = pd.to_datetime(all_df['date'])
    
    # 获取唯一的股票列表供切换 (你的需求 #1)
    available_tickers = all_df['ticker'].unique().tolist()
    selected_ticker = st.selectbox("🔍 选择要分析的股票", available_tickers)

    # 过滤选中的股票数据
    df = all_df[all_df['ticker'] == selected_ticker].sort_values('date')
    
    # 实时计算 Buzz Score
    df['buzz_score'] = df.apply(lambda r: calculate_buzz_score(r, vol_w, sent_w), axis=1)

    if not df.empty:
        # --- 核心指标卡 ---
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Buzz Score", last_row['buzz_score'], round(last_row['buzz_score']-prev_row['buzz_score'], 2))
        c2.metric("实时股价", f"${last_row['price']}", round(last_row['price']-prev_row['price'], 2))
        
        # 情绪指标展示 (你的需求 #3)
        sentiment_val = last_row['sentiment_avg']
        sentiment_label = "🔥 乐观" if sentiment_val > 0.55 else ("❄️ 悲观" if sentiment_val < 0.45 else "😐 中性")
        c3.metric("情绪状态", sentiment_label, f"{int(sentiment_val*100)}% 正向")
        
        c4.metric("社交提及量", int(last_row['mentions']))

        # --- 可视化图表 ---
        st.subheader(f"{selected_ticker} 深度关联趋势")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Buzz Score 曲线
        fig.add_trace(go.Scatter(x=df['date'], y=df['buzz_score'], name="Buzz Score", 
                                line=dict(color='#00f2fe', width=3)), secondary_y=False)
        
        # 股价曲线
        fig.add_trace(go.Scatter(x=df['date'], y=df['price'], name="股价 ($)", 
                                line=dict(color='#f12711', dash='dot')), secondary_y=True)

        fig.update_layout(template="plotly_dark", hovermode="x unified",
                          margin=dict(l=20, r=20, t=30, b=20),
                          legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

        # --- 情绪分布明细 ---
        st.markdown(f"**💡 情绪分析依据**：基于过去 24h 关于 {selected_ticker} 的最新新闻标题，通过 VADER 算法实时解析。")
        
    else:
        st.info("该股票暂无历史数据。")
else:
    st.error("未找到数据文件。请先运行 GitHub Action。")

st.markdown("---")
st.caption(f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据源: NewsAPI + yfinance")
