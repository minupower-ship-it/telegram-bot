from flask import Flask, request
import requests
import os
import sqlite3

app = Flask(__name__)

# ===== 기본 설정 =====
TOKEN = os.environ.get("BOT_TOKEN")
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

ADMIN_ID = 5619516265
DB_NAME = os.environ.get("DB_NAME", "users.db")

# ===== DB 초기화 =====
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_user(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# ✅ GET + POST 통합 (중요)
@app.route("/", methods=["GET", "POST"])
def main():
    # 서버 상태 확인용
    if request.method == "GET":
        return "Bot is running"

    # ===== Webhook =====
    update = request.get_json()
    if not update or "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    total_users = save_user(chat_id)

    if text == "/start":
        requests.post(f"{API_URL}/sendVideo", json={
            "chat_id": chat_id,
            "video": VIDEO_URL,
            "caption": CAPTION
        })

        keyboard = {
            "inline_keyboard": [
                [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
                [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
                [{"text": "❓ Proof here", "url": "https://t.me/MBRYPIE"}]
            ]
        }

        requests.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "PAYMENT METHOD\n\n💡 After payment, please send me a proof!",
            "reply_markup": keyboard
        })

    elif text == "/users":
        if chat_id == ADMIN_ID:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👥 총 유입 인원 수: {total_users}명"
            })
        else:
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ 관리자만 사용할 수 있습니다."
            })

    return "ok"

# ===== Render 실행 =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
