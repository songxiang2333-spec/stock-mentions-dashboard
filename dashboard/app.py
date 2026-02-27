import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import base64
import requests
import json
from datetime import datetime

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="AI Multi-Stock Intelligence", layout="wide", page_icon="🤖")

# --- 2. 核心功能函数：同步到 GitHub ---
def sync_to_github(file_path, content, message):
    token = os.environ.get('GH_TOKEN')
    repo = os.environ.get('REPO_NAME')
    if not token or not repo:
        st.error("❌ 环境变量未配置: 请在 Render 设置 GH_TOKEN 和 REPO_NAME")
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 获取旧文件的 SHA (更新必须)
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None

    # 提交新内容
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }
    put_res = requests.put(url, json=payload, headers=headers)
    return put_res.status_code in [200, 201]

# --- 3. 侧边栏：监控中心 ---
st.sidebar.title("🛠 控制面板")

# --- 核心修复点：先定义变量，再进行判断 ---
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
            st.sidebar.success(f"已识别 {len(tickers)} 只股票")
            
            # 点击按钮触发 GitHub 同步
            if st.sidebar.button("🚀 真正同步到云端监控"):
                csv_str = "Ticker\n" + "\n".join(tickers)
                if sync_to_github("data/targets.csv", csv_str, "Web update targets via Streamlit"):
                    st.sidebar.success("✅ 清单已同步！")
                else:
                    st.sidebar.error("❌ 同步失败，检查 Token 权限")
        else:
            st.sidebar.error("错误：文件中未找到 'Ticker' 列")
    except Exception as e:
        st.sidebar.error(f"解析失败: {e}")

st.sidebar.markdown("---")

# --- 4. 报警设定入口 ---
st.sidebar.subheader("🔔 动态提醒设定")
alert_threshold = st.sidebar.number_input("Buzz Score 报警阈值", value=1.2, step=0.1)
alert_email = st.sidebar.text_input("接收邮箱", placeholder="example@163.com")

if st.sidebar.button("💾 保存报警规则"):
    config_data = json.dumps({
        "alert_threshold": alert_threshold,
        "receiver_email": alert_email
    }, indent=4)
    if sync_to_github("data/config.json", config_data, "Web update config via Streamlit"):
        st.sidebar.success("✅ 报警规则已同步到云端")

# --- 5. 主界面数据逻辑 ---
st.title("📈 AI 股票热度与情绪监控系统")

file_path = 'data/history.csv'
if os.path.exists(file_path):
    all_df = pd.read_csv(file_path)
    # 此处省略之前的绘图逻辑，保持原样即可...
    # (确保 selected_ticker 等变量正常工作)
    available_tickers = all_df['ticker'].unique().tolist()
    selected_ticker = st.selectbox("🔍 选择要分析的股票", available_tickers)
    # ... 绘图代码 ...
else:
    st.info("数据文件正在生成中，请先运行 GitHub Action。")
