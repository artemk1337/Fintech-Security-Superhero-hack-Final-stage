
from private import TOKEN, telegram_admins, email_admins, TG, MAIL, MAC, USERNAME, PC_info
from email.mime.text import MIMEText
import requests
import smtplib


def send_via_telegram(content):

    for chat_id in telegram_admins:

        message  = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={content}'
        response = requests.get(message)
        status   = response.status_code

        if status != '200':
            # action
            pass

        try:
            data = response.json()
        except:
            # action
            pass

def send_via_email(content, subject='Test'):

    sender              = 'crewmate.adam.42@gmail.com'
    password            = '4T9-vz5-CLP-RiC'
    smtp                = smtplib.SMTP('smtp.gmail.com', 587)

    try:
        smtp.starttls()
        smtp.login(sender, password)

        for receiver in email_admins:
            message             = MIMEText(content)
            message['Subject']  = subject
            message['From']     = sender
            message['To']       = receiver
            message             = message.as_string()
            smtp.sendmail(sender, receiver, message)

        smtp.quit()

    except:

        # action
        pass


def send_msg(content, subject='Test'):
    content = content + f'\n\nUsername: {USERNAME}\nPC-info: {PC_info}\nMAC: {MAC}'
    if TG:
        send_via_telegram(content)

    if MAIL:
        send_via_email(content, subject=subject)