from flask import Flask, request
import requests
import os
import psycopg2

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

# ===== Render Postgres 연결 =====
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://telegram_db_ptfi_user:qD9rpyhC3HWWYGkZ5sXql3deAFNmTkHl@dpg-d54ajh75r7bs73eafrb0-a.virginia-postgres.render.com/telegram_db_ptfi"
)

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
conn.autocommit = True

# ===== 테이블 생성 =====
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

# ===== DB 함수 =====
def save_user(chat_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (chat_id)
            VALUES (%s)
            ON CONFLICT (chat_id) DO NOTHING
            """,
            (chat_id,)
        )

def get_user_count():
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

# ===== Webhook =====
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return "Bot is running"

    update = request.get_json()
    if not update or "message" not in update:
        return "ok"

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        save_user(chat_id)

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
            count = get_user_count()
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👥 총 유입 인원 수: {count}명"
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
