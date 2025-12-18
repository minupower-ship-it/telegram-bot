from flask import Flask, request
import requests
import os
import sqlite3

app = Flask(__name__)

# ===== 기본 설정 =====
TOKEN = os.environ.get("BOT_TOKEN")  # Render 환경변수 추천
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/dt49t2.mp4"

CAPTION = """
──────────────────────────────
Welcome to Private Collection
──────────────────────────────
• Only high quality handpicked content.
• Premium ★nlyFans Videos
• DECEMBER 2025: ★ ACTIVE ★
──────────────────────────────
★ Price: $20
★ INSTANT ACCESS ★
──────────────────────────────
"""

# ===== 관리자 Telegram ID =====
ADMIN_ID = 5619516265

# ===== DB 초기화 =====
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()  # 서버 시작 시 1번만 실행

# ===== 유저 저장 & 총 유입 수 =====
def save_user(chat_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (chat_id) VALUES (?)",
        (chat_id,)
    )
    conn.commit()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# ===== Webhook =====
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # 유저 저장
    total_users = save_user(chat_id)

    # ===== /start =====
    if text == "/start":
        # 영상 전송
        requests.post(f"{API_URL}/sendVideo",
            json={"chat_id": chat_id, "video": VIDEO_URL, "caption": CAPTION})

        # 버튼 전송
        keyboard = {
            "inline_keyboard": [
                [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
                [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
                [{"text": "❓ Proof here", "url": "https://t.me/MBRYPIE"}]
            ]
        }

        requests.post(f"{API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": "PAYMENT METHOD\n\n💡 After payment, please send me a proof!", "reply_markup": keyboard})

    # ===== /users (관리자용) =====
    elif text == "/users":
        if chat_id == ADMIN_ID:
            requests.post(f"{API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": f"👥 총 유입 인원 수: {total_users}명"})
        else:
            requests.post(f"{API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": "❌ 관리자만 사용할 수 있습니다."})

    return "ok"

# ===== 서버 상태 =====
@app.route("/", methods=["GET"])
def index():
    return "Bot is running"
