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
    # 读取最新数据
    df = pd.read_csv('data/history.csv')
    last_row = df.iloc[-1]
    
    ticker = last_row['ticker']
    buzz_score = last_row['mentions_growth'] # 这里先简单用增长率作为触发条件
    price = last_row['price']

    # 设定触发阈值：比如增长率超过 1.5 (即热度增加 50% 以上)
    if buzz_score > 1.5:
        subject = f"🚨 股票预警：{ticker} 社交热度异常！"
        body = f"股票代码: {ticker}\n当前价格: ${price}\n热度增长: {buzz_score}x\n\n检测到该股讨论量激增，请及时查看仪表板分析。"
        send_email(subject, body)
    else:
        print(f"指标正常 (Buzz: {buzz_score})，无需发送提醒。")

if __name__ == "__main__":
    check_alert()
