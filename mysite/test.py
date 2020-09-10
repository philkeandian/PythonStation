# -*- coding:utf-8 -*-
import os
from django.core.mail import send_mail


os.environ['DJANGO_SETTING_MODULE'] = 'mysite.settings'


if __name__ == '__main__':
    send_mail(
        '来自本地的测试邮件',
        '欢迎！',
        'XXX@XXX.com',
        ['XXX@XXX.com'],
    )

    """
    import smtplib
    from email.mime.text import MIMEText

    # 第三方 SMTP 服务
    mail_host = "XXX@XXX.com"  # SMTP服务器
    mail_user = "XXXX"  # 用户名
    mail_pass = "XXXX"  # 密码(这里的密码不是登录邮箱密码，而是授权码)

    sender = 'XXX@XXX.com'  # 发件人邮箱
    receivers = ['XXX@XXX.com']  # 接收人邮箱

    content = 'Python Send Mail !'
    title = 'Python SMTP Mail Test'  # 邮件主题
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)
    """
