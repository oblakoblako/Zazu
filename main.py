from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZMTECH_ID = os.environ.get("ZMTECH_ID", "140067")
ZMTECH_KEY = os.environ.get("ZMTECH_KEY", "ff2c5ae62e9f1d2615a1150d4962152aaaafbeb9")
ZMTECH_LOGIN = os.environ.get("ZMTECH_LOGIN", "89826872043")
ZMTECH_PASSWORD = os.environ.get("ZMTECH_PASSWORD", "9ix-JMa-2rE-En7")
ZMTECH_URL = "http://api.zmtech.ru:7777/v1/brand"

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
    try:
        response = requests.post(ZMTECH_URL, json=payload, timeout=10)
        raw = response.text
        try:
            return {"status": "ok", "response": response.json()}
        except Exception:
            return {"status": "ok", "raw_response": raw, "http_code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    phone = data.get("phone")
    text = data.get("message")

    if not phone or not text:
        return jsonify({"error": "phone and message required"}), 400

    result = send_sms(phone, text)
    return jsonify(result), 200

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
