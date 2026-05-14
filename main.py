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
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no json"}), 400

    # Телефон из contact.phone
    contact = data.get("contact", {})
    phone = contact.get("phone") if isinstance(contact, dict) else None

    # SMS текст из call.agreements.smsText
    call = data.get("call", {})
    if isinstance(call, dict):
        agreements = call.get("agreements", {})
        if isinstance(agreements, dict):
            text = agreements.get("smsText")
        else:
            text = None
    else:
        text = None

    # Запасной вариант если smsText пустой
    if not text:
        text = "Спасибо за звонок! Мы свяжемся с вами в ближайшее время."

    print(f"phone: {phone}, text: {text}")

    if not phone:
        return jsonify({"error": "phone not found", "contact":
