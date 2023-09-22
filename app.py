from flask import Flask, request, jsonify, render_template
import requests
import json
import hashlib
import random
import string
import time
import base64
import hmac

app = Flask(__name__)

# Replace with your actual Rapyd API keys
RAPYD_ACCESS_KEY = 'your_rapyd_access_key'
RAPYD_SECRET_KEY = 'your_rapyd_secret_key'

BASE_URL = 'https://sandboxapi.rapyd.net'

def generate_salt(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def create_signature(http_method, path, salt, timestamp, body=None):
    to_sign = (http_method, path, salt, str(timestamp), RAPYD_ACCESS_KEY, RAPYD_SECRET_KEY, body)
    h = hmac.new(RAPYD_SECRET_KEY.encode('utf-8'), ''.join(to_sign).encode('utf-8'), hashlib.sha256)
    signature = base64.urlsafe_b64encode(str.encode(h.hexdigest()))
    return signature

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_payment', methods=['POST'])
def create_payment():
    amount = request.form['amount']
    currency = request.form['currency']
    card_number = request.form['card_number']
    expiration_month = request.form['expiration_month']
    expiration_year = request.form['expiration_year']
    cvv = request.form['cvv']
    name = request.form['name']

    # Generate necessary headers
    timestamp = int(time.time())
    salt = generate_salt()
    url_path = '/v1/payments'
    http_method = 'post'

    body = json.dumps({
        'amount': amount,
        'currency': currency,
        'payment_method': {
            'type': 'gb_visa_card',
            'fields': {
                'number': card_number,
                'expiration_month': expiration_month,
                'expiration_year': expiration_year,
                'cvv': cvv, 
                'name': name
            }
        }
    }, separators=(',', ':'))

    signature = create_signature(http_method, url_path, salt, timestamp, body)

    headers = {
        'access_key': RAPYD_ACCESS_KEY,
        'salt': salt,
        'timestamp': str(timestamp),
        'signature': signature,
        'Content-Type': 'application/json'
    }

    response = requests.post(BASE_URL + url_path, headers=headers, data=body)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
