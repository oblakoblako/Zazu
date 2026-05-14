from flask import Flask, request, jsonify
import requests
import os

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

    print("FULL DATA:", data)

    # Достаём phone — пробуем разные уровни вложенности
    call_details = data.get("callDetails", {})
    agreements = data.get("agreements", {})

    phone = (
        call_details.get("destination_phone") or
        data.get("destination_phone") or
        data.get("phone")
    )

    text = (
        agreements.get("smsText") or
        data.get("smsText") or
        data.get("text") or
        data.get("message")
    )

    print(f"phone: {phone}, text: {text}")

    if not phone:
        return jsonify({"error": "phone not found", "data": data}), 400
    if not text:
        return jsonify({"error": "smsText not found", "data": data}), 400

    result = send_sms(phone, text)
    return jsonify(result), 200

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
