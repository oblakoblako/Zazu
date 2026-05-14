from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

ZMTECH_ID = os.environ.get("ZMTECH_ID", "140067")
ZMTECH_KEY = os.environ.get("ZMTECH_KEY", "ff2c5ae62e9f1d2615a1150d4962152aaaafbeb9")
ZMTECH_URL = "http://api.zmtech.ru:7777/v1/brand"

def send_sms(phone, text, sender="INFO"):
    payload = {
        "id": ZMTECH_ID,
        "password": ZMTECH_KEY,
        "pack": [{"phone": phone, "text": text, "sender": sender}]
    }
    try:
        response = requests.post(ZMTECH_URL, json=payload, timeout=10)
        try:
            return {"status": "ok", "response": response.json()}
        except Exception:
            return {"status": "ok", "raw_response": response.text, "http_code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.data.decode("utf-8")
    print("=== RAW BODY ===")
    print(raw[:3000])  # первые 3000 символов

    data = request.get_json(silent=True)
    print("=== TOP LEVEL KEYS ===")
    if data:
        print(list(data.keys()))
        for key in data.keys():
            val = data[key]
            print(f"  {key}: {type(val).__name__} = {str(val)[:200]}")
    
    return jsonify({"status": "logged"}), 200

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
