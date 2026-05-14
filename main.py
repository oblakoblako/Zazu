# main.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ZMTECH_ID = "140067"
ZMTECH_KEY = "ff2c5ae62e9f1d2615a1150d4962152aaaafbeb9"
ZMTECH_URL = "http://api.zmtech.ru:7777/v1/brand"

ZMTECH_LOGIN = "89826872043"
ZMTECH_PASSWORD = "9ix-JMa-2rE-En7"

def send_sms(phone, text, sender="INFO"):
    payload = {
        "id": ZMTECH_LOGIN,
        "password": ZMTECH_PASSWORD,
        "pack": [
            {
                "phone": phone,
                "text": text,
                "sender": sender
            }
        ]
    }
    response = requests.post(ZMTECH_URL, json=payload)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    phone = data.get("phone")
    text = data.get("message")

    if not phone or not text:
        return jsonify({"error": "phone and message required"}), 400

    result = send_sms(phone, text)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
