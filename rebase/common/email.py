from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import info
from smtplib import SMTP_SSL

from flask import current_app


class Email(object):

    def __init__(self, from_addr, to_addrs, subject, text_msg, html_msg):
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        _msg = MIMEMultipart('alternative')
        _msg['Subject'] = subject
        _msg['From'] = 'do_not_reply@rebaseapp.com'
        _msg['To'] = ','.join(to_addrs)
        html = """\
        <html>
            <head></head>
            <body>
                <title href='{app_url}'>Rebase</title>
                <p>
                {text}
                </p>
            </body>
        </html>
        """.format(app_url='{{APP_URL}}', text=html_msg)
        _msg.attach(MIMEText(text_msg, 'plain'))
        _msg.attach(MIMEText(html, 'html'))
        self.msg = _msg.as_string()

    def __str__(self):
        return 'from: {}, to: {}, msg: {}'.format(self.from_addr, self.to_addrs, self.msg)


def send_emails(emails, smtp_host, smtp_login, smtp_password):
    server = SMTP_SSL(smtp_host)
    server.login(smtp_login, smtp_password)
    for email in emails:
        isinstance(email, Email)
        info('Sending email: %s', email)
        server.sendmail(email.from_addr, email.to_addrs, email.msg)
    server.quit()


def send(emails):
    current_app.default_queue.enqueue(
        send_emails,
        emails,
        '',
        '',
        ''
        #current_app.config.SMTP_HOST,
        #current_app.config.NOTIFICATION_EMAIL,
        #current_app.config.NOTIFICATION_EMAIL_PASSWORD
    )


