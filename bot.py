from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["8511250034:AAGTKkLILZ0MkMd6IkEoxcX1d5tEcLXYeNU"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/dt49t2.mp4"  # ⚠️ pbz.mp4는 서버에 없으니 URL 필요

CAPTION = """
──────────────────────────────

Welcome to Private Collection

──────────────────────────────

• Only high quality handpicked content.

• Premium ★nlyFans Videos  
  (All models you can imagine)

• DECEMBER 2025: ★ ACTIVE ★

──────────────────────────────

★ Price: $20

★ INSTANT ACCESS ★

──────────────────────────────
"""

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            # 비디오 전송
            requests.post(
                f"{API_URL}/sendVideo",
                json={
                    "chat_id": chat_id,
                    "video": VIDEO_URL,
                    "caption": CAPTION
                }
            )

            # 버튼 메시지
            keyboard = {
                "inline_keyboard": [
                    [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
                    [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
                    [{"text": "❓ HELP", "url": "https://t.me/MBRYPIE"}]
                ]
            }

            requests.post(
                f"{API_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "PAYMENT METHOD\n\n💡 After payment, please send me a proof!",
                    "reply_markup": keyboard
                }
            )

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"