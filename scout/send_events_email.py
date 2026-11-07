"""Send the monthly academic-events email through Gmail.

Usage:  python3 -I -X utf8 scout/send_events_email.py <email.html> "<subject>"
Reads GMAIL_USER, GMAIL_APP_PASSWORD and EMAIL_TO from the environment
(same GitHub secrets the Morning Markets Brief uses).
EMAIL_TO may hold several addresses separated by commas.
"""
import os, sys, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

html_path, subject = sys.argv[1:3]
user = os.environ.get('GMAIL_USER', '').strip()
password = os.environ.get('GMAIL_APP_PASSWORD', '').replace(' ', '').strip()
to = [a.strip() for a in os.environ.get('EMAIL_TO', '').split(',') if a.strip()]
if not (user and password and to):
    sys.exit('Email skipped: GMAIL_USER, GMAIL_APP_PASSWORD or EMAIL_TO is not set.')

html = open(html_path, encoding='utf-8').read()
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = f'Academic Events Scout <{user}>'
msg['To'] = ', '.join(to)
msg.attach(MIMEText(f'Your monthly academic events scan is ready: {subject}\n'
                    'Everything is in the email below, organised by city.\n', 'plain', 'utf-8'))
msg.attach(MIMEText(html, 'html', 'utf-8'))

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context(), timeout=60) as s:
    s.login(user, password)
    s.sendmail(user, to, msg.as_string())
print(f'Email sent to {len(to)} recipient(s), {len(html)} chars.')
