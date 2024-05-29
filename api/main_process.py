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
from flask import jsonify
from dotenv import load_dotenv

load_dotenv('environment.env')

# main workflow
def process_post(data):
    try:
        batch = BatchPost(data)
        blackbaud(batch)
        if not batch.has_emails:
            print('No emails found')
            return jsonify(message="No emails found.")

        drip(batch)

        if batch.notif_email and batch.tag != 'test_only':
            batch.gen_message()
            send_email(batch.notif_email, batch.cc, batch.message, batch.batch, batch.tag_state)

        return jsonify(**batch.gen_resp()), 200

    except Exception as e:
        message = e
        print(e)
        cc = os.environ.get('ADMIN')
        notification_email = batch.notif_email if batch.notif_email else cc
        batch = batch if batch else ''
        send_email(notification_email, cc, message, batch.batch, batch.tag_state)
        error_msg = "The server failed. A notification with logs was sent to you and the admin."
        return jsonify(message=error_msg, outcome="Operation Failed"), 500

if __name__ == "__main__":
    from test_names import names
    test_data = names
    process_post(test_data)
