try:
    from api.blackbaud import blackbaud
    from api.email_confirm import send_email
    from api.drip import drip
    from api.batch_post import BatchPost
except ModuleNotFoundError:
    from blackbaud import blackbaud
    from email_confirm import send_email
    from drip import drip
    from batch_post import BatchPost
import os
from flask import jsonify, Response
import requests
from dotenv import load_dotenv

load_dotenv('environment.env')

def process_post(data: dict) -> Response:
    """
    Take a POST from NXT, retrieve emails and consent from NXT, make tags in drip, send email,
    and return results to NXT extension.
    data: the body of the POST
    Response: the outcome of the processing
    """
    try:
        # Make BatchPost object from data
        batch = BatchPost(data)

        # Look up email addresses and consent with NXT API
        blackbaud(batch)

        if not batch.has_emails:
            print('No emails found')
            return jsonify(message="No emails found.")

        # Tag or untag emails in Drip
        drip(batch)

        # Generate a confirmation email and send it.
        if batch.notif_email and batch.tag != 'test_only':
            batch.gen_message()
            send_email(batch.notif_email, batch.cc, batch.message, batch.batch, batch.tag_state)

        # Return results to extension in NXT.
        return jsonify(**batch.gen_resp()), 200

    except requests.exceptions.Timeout as message:
        print(message)

        admin = os.environ.get('ADMIN') # Retrieve admin email

        # If the user didn't sign up for notification, notify admin anyway
        notification_email = batch.notif_email if batch.notif_email else admin
        send_email(notification_email, admin, message, batch.batch, batch.tag_state)

        # Return error message to NXT extension.
        error_msg = "The server failed. A notification with logs was sent to you and the admin."
        return jsonify(message=error_msg, outcome="Operation Failed"), 500

if __name__ == "__main__":
    from test_names import names
    test_data = names
    print(names)
    batch = BatchPost(names)
    blackbaud(batch)
