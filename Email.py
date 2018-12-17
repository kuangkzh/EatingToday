import smtplib
from email.mime.text import MIMEText
from email.header import Header


# fixme
sender = ""
password = ""


def send_plain_text(receivers, text, subject=None, _from=None, _to=None):
    message = MIMEText(text, 'plain', 'utf-8')
    if _from:
        message['From'] = Header(_from, 'utf-8')  # 发送者
    if _to:
        message['To'] = Header(_to, 'utf-8')  # 接收者
    if subject:
        message['Subject'] = Header(subject, 'utf-8')   # 主题
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, password)
    server.sendmail(sender, receivers, message.as_string())
    server.quit()
