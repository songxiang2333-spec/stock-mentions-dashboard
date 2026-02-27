
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import os

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('RECEIVER_EMAIL')

    try:
        # 如果用QQ邮箱，服务器是 smtp.qq.com；163是 smtp.163.com
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))
            server.send_message(msg)
        print("✅ 邮件提醒已发送")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def check_alert():
    if not os.path.exists('data/history.csv'):
        print("数据文件不存在，跳过提醒。")
        return

    df = pd.read_csv('data/history.csv')
    
    # 核心修复：如果数据少于 1 行，直接退出
    if len(df) < 1:
        print("数据不足，无法进行分析。")
        return

    last_row = df.iloc[-1]
    ticker = last_row['ticker']
    # 注意：确保这里引用的列名和你 CSV 里的表头完全一致
    buzz_score = last_row['mentions_growth'] 
    price = last_row['price']

    # 触发逻辑
    if buzz_score > 1.5:
        subject = f"🚨 股票预警：{ticker} 社交热度异常！"
        body = f"股票代码: {ticker}\n当前价格: ${price}\n热度增长: {buzz_score}x"
        send_email(subject, body)
    else:
        print(f"指标正常 (Buzz: {buzz_score})")
if __name__ == "__main__":
    check_alert()
