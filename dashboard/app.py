import base64
import requests
import json

# --- GitHub 同步函数 ---
def sync_to_github(file_path, content, message):
    token = os.environ.get('GH_TOKEN')
    repo = os.environ.get('REPO_NAME')
    if not token or not repo:
        st.error("未配置 GH_TOKEN 或 REPO_NAME 环境变量")
        return False

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # 1. 获取旧文件 SHA (更新必须)
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None

    # 2. 提交新内容
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }
    put_res = requests.put(url, json=payload, headers=headers)
    return put_res.status_code in [200, 201]

# --- 修改侧边栏上传部分 ---
if uploaded_file is not None:
    # ... 原有的解析代码 (得到 tickers 列表) ...
    if st.sidebar.button("🚀 真正同步到云端监控"):
        csv_str = "Ticker\n" + "\n".join(tickers)
        if sync_to_github("data/targets.csv", csv_str, "Web update targets"):
            st.sidebar.success("✅ 清单已同步！明早 8 点自动采集。")
        else:
            st.sidebar.error("❌ 同步失败，请检查 Token 权限。")

# --- 修改报警设定部分 ---
st.sidebar.subheader("🔔 动态提醒设定")
# ... 原有的 input 代码 ...
if st.sidebar.button("💾 保存报警规则"):
    config_data = json.dumps({
        "alert_threshold": alert_threshold,
        "receiver_email": alert_email
    }, indent=4)
    if sync_to_github("data/config.json", config_data, "Web update config"):
        st.sidebar.success("✅ 报警规则已生效。")
