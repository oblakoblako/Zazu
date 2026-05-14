from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZMTECH_ID = os.environ.get("ZMTECH_ID", "140067")
ZMTECH_KEY = os.environ.get("ZMTECH_KEY", "ff2c5ae62e9f1d2615a1150d4962152aaaafbeb9")
ZMTECH_URL = "http://api.zmtech.ru:7777/v1/brand"


def send_sms(phone, text):
    payload = {
        "id": ZMTECH_ID,
        "password": ZMTECH_KEY,
        "pack": [{"phone": phone, "text": text, "sender": "INFO"}]
    }
    try:
        r = requests.post(ZMTECH_URL, json=payload, timeout=10)
        try:
            return {"status": "ok", "response": r.json()}
        except Exception:
            return {"status": "ok", "raw": r.text, "code": r.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no json"}), 400

    contact = data.get("contact") or {}
    phone = contact.get("phone") if isinstance(contact, dict) else None

    call = data.get("call") or {}
    if isinstance(call, dict):
        agreements = call.get("agreements") or {}
        text = agreements.get("smsText") if isinstance(agreements, dict) else None
    else:
        text = None

    if not text:
        text = "Спасибо за звонок! Мы свяжемся с вами в ближайшее время."

    print("phone:", phone, "text:", text)

    if not phone:
        return jsonify({"error": "phone not found"}), 400

    result = send_sms(phone, text)
    return jsonify(result), 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
