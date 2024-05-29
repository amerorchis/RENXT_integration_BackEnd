from flask import Flask, request
from api.main_process import process_post
import os
from flask_cors import CORS

# Main app route

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://host.nxt.blackbaud.com"}})
env_variable = os.environ.get('TEST_VARIABLE', '')

@app.route('/', methods=['GET', 'POST'])
def handle_requests():
    if request.method == 'GET':
        return env_variable + ". Make a POST request to use this program." if env_variable else 'No env variable found.'

    elif request.method == 'POST':
        r = process_post(request.json)
        print(r)
        return r

    elif request.method == 'OPTIONS':
        return 200
