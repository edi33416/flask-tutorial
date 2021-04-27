from threading import Thread

from flask import current_app
from flask_mail import Message

from app import mail

def send_async_email(app, msg):
    # App context is required so flask_mail can access config vars
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    # current_app is tied to the current thread.
    # access the underlying app object when spwaning a new thread
    Thread(target = send_async_email, args = (current_app._get_current_object(), msg)).start()
