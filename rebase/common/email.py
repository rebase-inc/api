from logging import info
from smtplib import SMTP_SSL

from flask.ext.login import current_app
from flask import current_app


class Email(object):

    def __init__(self, from_addr, to_addrs, msg=''):
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.msg = msg

    def __str__(self):
        return 'from: {}, to: {}, msg: {}'.format(self.from_addr, self.to_addrs, self.msg)


def _send(emails, login_email, login_password):
    server = SMTP_SSL('smtp.gmail.com')
    server.login(login_email, login_password)
    for email in emails:
        isinstance(email, Email)
        info('Sending email: %s', email)
        server.sendmail(email.from_addr, email.to_addrs, email.msg)
    server.quit()


def send(emails):
    current_app.default_queue.enqueue(
        _send,
        emails,
        current_app.config['NOTIFICATION_EMAIL'],
        current_app.config['NOTIFICATION_EMAIL_PASSWORD']
    )


