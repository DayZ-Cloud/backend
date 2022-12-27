import smtplib
import os
from email.mime.text import MIMEText

EMAIL_HOST = 'smtp.yandex.ru'


def send_email(text, email):
    message = MIMEText(text, 'plain')
    message["Subject"] = "Ваше лисье величество"
    message["From"] = "darklorian@darklorian.ru"

    conn = smtplib.SMTP_SSL(EMAIL_HOST)
    conn.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
    conn.sendmail("darklorian@darklorian.ru", [email], message.as_string())