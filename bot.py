from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/dt49t2.mp4"

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

COUNT_FILE = "count.txt"

# 관리자 ID (여기에 @mbrypie 숫자 ID 넣기)
ADMIN_ID = 5619516265  # <-- BotFather에서 확인한 숫자 ID 넣으세요

def increment_count():
    try:
        with open(COUNT_FILE, "r") as f:
            count = int(f.read())
    except:
        count = 0
    count += 1
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))
    return count

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # 메시지 카운트 증가
        increment_count()

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
                    [{"text": "Proof here", "url": "https://t.me/MBRYPIE"}]
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

        elif text == "/count":
            if chat_id == ADMIN_ID:
                try:
                    with open(COUNT_FILE, "r") as f:
                        count = f.read()
                except:
                    count = "0"
                requests.post(
                    f"{API_URL}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": f"총 메시지 수: {count}"
                    }
                )
            else:
                requests.post(
                    f"{API_URL}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "❌ 이 명령어는 관리자만 사용할 수 있습니다."
                    }
                )

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

