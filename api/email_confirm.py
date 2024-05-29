import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(notification_email, cc, body_message, batch, tag_state):
    req_type = 'Tag' if tag_state else 'Untag'
    sender_email = os.environ['EMAIL']
    sender_pw = os.environ['EMAIL_PW']

    # Sender and recipient info
    sender_name = "Tag Confirmation"
    receiver_email = notification_email

    # Message details
    body = body_message

    # Create a multipart message
    message = MIMEMultipart()

    # Add sender, recipient, and cc headers to the message
    message['From'] = sender_name + " <" + sender_email + ">"
    message['To'] = receiver_email
    if cc:
        message['Cc'] = cc

    # Add subject and body to the message
    message['Subject'] = f'Constituents from {batch} {req_type}ged'
    message.attach(MIMEText(body, 'plain'))

    # Set up SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_pw)

    # Send email
    if cc:
        server.sendmail(sender_email, [receiver_email, cc], message.as_string())
    else:
        server.sendmail(sender_email, receiver_email, message.as_string())

    server.quit()
    print('Email sent.')
