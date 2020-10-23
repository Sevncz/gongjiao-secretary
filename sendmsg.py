#!/usr/bin/python
# coding: utf-8
# __author__ = 'SevnCZ'
# __email__ = "wecz0321@gmail.com"
# __copyright__ = "Copyright 2019, SevnCZ"

import yagmail
from twilio.rest import Client


yag = yagmail.SMTP(user='xxx@qq.com', password='password', host='smtp.qq.com', port='465')

def send_email(msg):
    yag.send(to='xxx@live.com', subject='到站咯', contents=[msg])
    print("已发送邮件")


account_sid='AC905b19fa8e74244a07bcc9ec8f90b86b'
auth_token='f436aaa51a476c234897497500553719'

client = Client(account_sid, auth_token)

my_number='+861860075xxxx'
twilio_number='+1267297aaaa'

def send_sms_myself(content):
    message = client.messages \
        .create(
        body=content,
        from_=twilio_number,
        to=my_number
    )
    print(message.sid)


if __name__ == "__main__":
    send_sms_myself("hello")