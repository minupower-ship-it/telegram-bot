from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ===== 기본 설정 =====
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

# ===== 파일 =====
USERS_FILE = "users.txt"   # 유입된 사람(chat_id)만 저장

# ===== 관리자 Telegram 숫자 ID =====
ADMIN_ID = 5619516265   # ← 너 숫자 ID

# ===== 유저 저장 함수 =====
def save_user(chat_id):
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    except:
        users = []

    if str(chat_id) not in users:
        users.append(str(chat_id))
        with open(USERS_FILE, "w") as f:
            f.write("\n".join(users))

    return len(users)


# ===== Webhook =====
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # 유입 유저 저장 (중복 제거)
    save_user(chat_id)

    # ===== /start =====
    if text == "/start":
        # 영상 전송
        requests.post(
            f"{API_URL}/sendVideo",
            json={
                "chat_id": chat_id,
                "video": VIDEO_URL,
                "caption": CAPTION
            }
        )

        # 버튼
        keyboard = {
            "inline_keyboard": [
                [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
                [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
                [{"text": "❓ Proof here", "url": "https://t.me/MBRYPIE"}]
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

    # ===== 유입 인원 수 확인 =====
    elif text == "/users":
        if chat_id == ADMIN_ID:
            try:
                with open(USERS_FILE, "r") as f:
                    users = f.read().splitlines()
                count = len(users)
            except:
                count = 0

            requests.post(
                f"{API_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"👥 총 유입 인원 수: {count}명"
                }
            )
        else:
            requests.post(
                f"{API_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "❌ 관리자만 사용할 수 있습니다."
                }
            )

    return "ok"


# ===== 서버 상태 =====
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"

