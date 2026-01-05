from flask import Flask, request
import requests
import os
import psycopg2
import urllib.parse as up
from datetime import datetime

app = Flask(__name__)

# ================= 기본 설정 =================
TOKEN = os.environ.get("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/3f3sul.mp4"
ADMIN_ID = 5619516265

CRYPTO_QR = "https://files.catbox.moe/fkxh5l.png"
CRYPTO_ADDRESS = "TERhALhVLZRqnS3mZGhE1XgxyLnKHfgBLi"

# ================= DB 연결 =================
DATABASE_URL = os.environ.get("DATABASE_URL")

up.uses_netloc.append("postgres")
url = up.urlparse(DATABASE_URL)

conn = psycopg2.connect(
    dbname=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
conn.autocommit = True

# ================= DB 마이그레이션 =================
def migrate_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY
            )
        """)
    print("DB ready")

migrate_db()

# ================= DB 함수 =================
def save_user(chat_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (chat_id)
            VALUES (%s)
            ON CONFLICT (chat_id) DO NOTHING
        """, (chat_id,))

def get_user_count():
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

# ================= 키보드 =================
def join_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "Membership Join", "callback_data": "join"}]
        ]
    }

def payment_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
            [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
            [{"text": "🪙 USDT (TRON)", "callback_data": "crypto"}],
            [{"text": "🆘 Help", "url": "https://t.me/mbrypie"}]
        ]
    }

# ================= Webhook =================
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Bot running"

    update = request.get_json()
    if not update:
        return "ok"

    # ---------- 메시지 처리 ----------
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        command = text.split()[0] if text else ""

        # /start (payload 대응)
        if command == "/start":
            save_user(chat_id)

            requests.post(f"{API_URL}/sendVideo", json={
                "chat_id": chat_id,
                "video": VIDEO_URL,
                "reply_markup": join_keyboard()
            })

        elif command == "/users" and chat_id == ADMIN_ID:
            count = get_user_count()
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👥 Total users: {count}"
            })

    # ---------- 버튼 처리 ----------
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["from"]["id"]
        data = cq["data"]

        # 로딩 종료
        requests.post(f"{API_URL}/answerCallbackQuery", json={
            "callback_query_id": cq["id"]
        })

        if data == "join":
            today = datetime.now().strftime("%b %d")

            text = (
                "💎 Lifetime Entry — $20\n\n"
                f"{today} — ON\n"
                "Immediate access — ON"
            )

            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": payment_keyboard()
            })

        elif data == "crypto":
            requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id,
                "photo": CRYPTO_QR,
                "caption": f"USDT (TRON)\n\n{CRYPTO_ADDRESS}"
            })

    return "ok"

# ================= 실행 =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
