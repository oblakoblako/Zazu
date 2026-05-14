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
    raw = request.data.decode("utf-8")
    
    # Логируем что пришло от Sasha AI
    print("=== INCOMING WEBHOOK ===")
    print("RAW:", raw)
    print("JSON:", data)
    
    if not data:
        return jsonify({"error": "no json", "raw": raw}), 400

    # Пробуем разные возможные поля с номером телефона
    phone = (data.get("phone") or data.get("contact_phone") or 
             data.get("lead_phone") or data.get("number") or
             data.get("client_phone"))
    text = (data.get("message") or data.get("text") or 
            data.get("sms_text") or "Вам перезвонят")

    if not phone:
        return jsonify({"error": "phone not found", "received_data": data}), 400

    result = send_sms(phone, text)
    return jsonify(result), 200

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
