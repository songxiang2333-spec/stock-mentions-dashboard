import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import base64
import requests
import json
from datetime import datetime

# --- 1. 变量初始化 (解决 NameError 的关键) ---
uploaded_file = None 
selected_ticker = "NVDA"

# --- 2. 页面基本配置 ---
st.set_page_config(page_title="AI Multi-Stock Intelligence", layout="wide", page_icon="🤖")

# --- 3. 核心功能函数：同步数据到 GitHub ---
def sync_to_github(file_path, content, message):
    """
    通过 GitHub API 将内容写入仓库文件
    """
    token = os.environ.get('GH_TOKEN')
    repo = os.environ.get('REPO_NAME')
    
    if not token or not repo:
        st.error("❌ 环境错误: 请在 Render 设置中配置 GH_TOKEN 和 REPO_NAME")
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 获取旧文件的 SHA (更新文件必须带 SHA)
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None

    # 准备提交
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }
    
    put_res = requests.put(url, json=payload, headers=headers)
    return put_res.status_code in [200, 201]

# --- 4. 侧边栏：监控中心 ---
st.sidebar.title("🛠 控制面板")

# A. 上传清单逻辑
st.sidebar.subheader("上传监控清单")
# 确保赋值语句在任何判断之前
uploaded_file = st.sidebar.file_uploader("导入 Excel/CSV (需包含 Ticker 列)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            upload_df = pd.read_excel(uploaded_file)
        else:
            upload_df = pd.read_csv(uploaded_file)
        
        if 'Ticker' in upload_df.columns:
            tickers_list = upload_df['Ticker'].dropna().unique().tolist()
            st.sidebar.success(f"已识别 {len(tickers_list)} 只股票")
            
            if st.sidebar.button("🚀 同步到云端监控"):
                csv_str = "Ticker\n" + "\n".join(tickers_list)
                if sync_to_github("data/targets.csv", csv_str, "Web update targets"):
                    st.sidebar.success("✅ 清单已同步！数据将在下次运行后更新。")
        else:
            st.sidebar.error("错误：文件中未找到 'Ticker' 列")
    except Exception as e:
        st.sidebar.error(f"解析失败: {e}")

st.sidebar.markdown("---")

# B. 报警设定逻辑
st.sidebar.subheader("🔔 动态提醒设定")
# 尝试读取现有配置作为默认值
alert_threshold = st.sidebar.number_input("Buzz Score 报警阈值", value=1.2, step=0.1)
alert_email = st.sidebar.text_input("接收邮箱", placeholder="your_email@163.com")

if st.sidebar.button("💾 保存报警规则"):
    config_dict = {
        "alert_threshold": alert_threshold,
        "receiver_email": alert_email
    }
    if sync_to_github("data/config.json", json.dumps(config_dict, indent=4), "Web update config"):
        st.sidebar.success("✅ 报警规则已同步到云端")

# --- 5. 主界面：可视化分析 ---
st.title("📈 AI 股票热度与情绪监控系统")

history_file = 'data/history.csv'
if os.path.exists(history_file):
    all_df = pd.read_csv(history_file)
    all_df['date'] = pd.to_datetime(all_df['date'])
    
    # 获取唯一的股票列表
    available_tickers = sorted(all_df['ticker'].unique().tolist())
    selected_ticker = st.selectbox("🔍 选择要分析的股票", available_tickers)

    # 过滤数据
    df = all_df[all_df['ticker'] == selected_ticker].sort_values('date')
    
    # 简单的 Buzz Score 计算预览 (权重与采集端对齐)
    df['buzz_score'] = (df['mentions_growth'] * 0.7) + ((df['sentiment_avg'] - 0.5) * 0.3)

    if not df.empty:
        # 指标卡
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Buzz Score", round(last['buzz_score'], 2), round(last['buzz_score']-prev['buzz_score'], 2))
        c2.metric(f"{selected_ticker} 价格", f"${last['price']}", round(last['price']-prev['price'], 2))
        c3.metric("情绪分", f"{int(last['sentiment_avg']*100)}% 正向")

        # 趋势图
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df['date'], y=df['buzz_score'], name="Buzz Score", line=dict(color='#00f2fe')), secondary_y=False)
        fig.add_trace(go.Scatter(x=df['date'], y=df['price'], name="股价", line=dict(color='#f12711', dash='dot')), secondary_y=True)
        fig.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ 暂无历史数据，请点击 GitHub Actions 运行数据采集。")
