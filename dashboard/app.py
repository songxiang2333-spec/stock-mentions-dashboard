import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 核心计算函数 ---
def calculate_buzz_score(row, vol_weight, sent_weight):
    """
    Buzz Score 计算逻辑:
    Score = (提及量增长率 * 体积权重) + (情绪均值 * 情绪权重)
    """
    # 确保数据为数值型，处理可能出现的缺失值
    growth = float(row.get('mentions_growth', 1.0))
    sentiment = float(row.get('sentiment_avg', 0.0))
    score = (growth * vol_weight) + (sentiment * sent_weight)
    return round(score, 2)

# --- 页面基础配置 ---
st.set_page_config(page_title="Stock Buzz Dashboard", layout="wide", page_icon="📈")

# --- 界面标题 ---
st.title("🚀 Stock Mentions & Market Analysis Dashboard")
st.markdown("---")

# --- 侧边栏控制面板 ---
st.sidebar.header("📊 系统配置")
ticker_input = st.sidebar.text_input("股票代码", "NVDA").upper()

st.sidebar.subheader("算法权重微调")
vol_w = st.sidebar.slider("提及量增长权重 (Volume)", 0.0, 1.0, 0.7)
sent_w = st.sidebar.slider("情绪正向权重 (Sentiment)", 0.0, 1.0, 0.3)

st.sidebar.info("提示：Buzz Score 越高，代表社交媒体讨论热度相对于平时越异常。")

# --- 数据读取与处理 ---
file_path = 'data/history.csv'

if not os.path.exists(file_path):
    st.warning(f"⚠️ 未找到数据文件 `{file_path}`。请先运行一次 GitHub Action 进行数据采集。")
else:
    try:
        # 读取 CSV 并确保数据类型正确
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date') # 确保时间轴顺序正确
        
        # 应用用户微调的权重计算实时 Buzz Score
        df['buzz_score'] = df.apply(lambda r: calculate_buzz_score(r, vol_w, sent_w), axis=1)

        # 数据量检查
        if len(df) > 0:
            # 1. 顶层核心指标 (Metrics)
            last_row = df.iloc[-1]
            
            # 只有当数据点大于2个时，才计算 Delta（涨跌幅）
            if len(df) >= 2:
                prev_row = df.iloc[-2]
                buzz_delta = round(last_row['buzz_score'] - prev_row['buzz_score'], 2)
                price_delta = round(last_row['price'] - prev_row['price'], 2)
            else:
                buzz_delta = 0
                price_delta = 0

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("当前 Buzz Score", last_row['buzz_score'], buzz_delta)
            with m_col2:
                st.metric(f"实时价格 ({ticker_input})", f"${last_row['price']}", price_delta)
            with m_col3:
                st.metric("24h 社交提及量", int(last_row['mentions']))

            # 2. 双轴可视化关联图表
            st.subheader("💡 关联性趋势分析：热度 vs 价格")
            
            # 创建带次坐标轴的图表
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 绘制 Buzz Score (左轴)
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['buzz_score'], name="Buzz Score (热度)", 
                           line=dict(color='#00CCFF', width=3), mode='lines+markers'),
                secondary_y=False,
            )

            # 绘制 股价 (右轴)
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['price'], name="Stock Price (股价)", 
                           line=dict(color='#FF3399', dash='dot'), mode='lines'),
                secondary_y=True,
            )

            # 布局美化
            fig.update_layout(
                template="plotly_dark",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=50, b=20),
                hovermode="x unified"
            )
            
            fig.update_yaxes(title_text="Buzz Score (Sentiment + Volume)", secondary_y=False)
            fig.update_yaxes(title_text="Price ($ USD)", secondary_y=True)

            st.plotly_chart(fig, use_container_width=True)

            # 3. 数据明细
            with st.expander("📂 查看完整历史数据报表"):
                st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
                
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 导出分析数据 (CSV)",
                    data=csv_data,
                    file_name=f"{ticker_input}_buzz_report.csv",
                    mime='text/csv',
                )

        else:
            st.info("CSV 文件已创建，但目前暂无有效行数据。请等待自动化脚本运行。")

    except Exception as e:
        st.error(f"⚠️ 数据处理出错: {e}")
        st.info("请检查 `data/history.csv` 的表头和内容格式是否正确。")

# --- 页脚 ---
st.markdown("---")
st.caption("数据来源：yfinance, GitHub Actions 模拟采集。系统每24小时自动更新。")
