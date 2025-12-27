from flask import Flask, request
import requests
import os
import psycopg2
import urllib.parse as up

app = Flask(__name__)

# ================= 기본 설정 =================
TOKEN = os.environ.get("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/dt49t2.mp4"

ADMIN_ID = 5619516265

CRYPTO_QR = "https://files.catbox.moe/fkxh5l.png"
CRYPTO_ADDRESS = "TERhALhVLZRqnS3mZGhE1XgxyLnKHfgBLi"

# ================= 캡션 =================
CAPTIONS = {
    "EN": """──────────────────────────────

Welcome to Private Collection

──────────────────────────────

• Only high quality handpicked content.

• Premium ★nlyFans Videos

• DECEMBER 2025: ★ ACTIVE ★

──────────────────────────────

★ Price: $20

★ INSTANT ACCESS ★

──────────────────────────────""",

    "FR": """──────────────────────────────

Bienvenue dans la Collection Privée

──────────────────────────────

• Contenu sélectionné de haute qualité uniquement.

• Vidéos Premium ★nlyFans

• DÉCEMBRE 2025 : ★ ACTIF ★

──────────────────────────────

★ Prix : 20$

★ ACCÈS INSTANTANÉ ★

──────────────────────────────""",

    "ZH": """──────────────────────────────

私人收藏欢迎您

──────────────────────────────

• 仅高质量精选内容

• 高级 ★nlyFans 视频

• 2025年12月：★ 活跃 ★

──────────────────────────────

★ 价格：$20

★ 即刻访问 ★

──────────────────────────────""",

    "AR": """──────────────────────────────

مرحبًا بك في المجموعة الخاصة

──────────────────────────────

• محتوى مختار عالي الجودة فقط

• فيديوهات ★nlyFans المميزة

• ديسمبر 2025: ★ نشط ★

──────────────────────────────

★ السعر: 20$

★ الوصول الفوري ★

──────────────────────────────""",

    "ES": """──────────────────────────────

Bienvenido a la Colección Privada

──────────────────────────────

• Solo contenido seleccionado de alta calidad

• Videos Premium ★nlyFans

• DICIEMBRE 2025: ★ ACTIVO ★

──────────────────────────────

★ Precio: $20

★ ACCESO INSTANTÁNEO ★

──────────────────────────────"""
}

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


# ================= DB 마이그레이션 (자동 실행) =================
def migrate_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY
            )
        """)
        cur.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'EN'
        """)
    print("DB migration completed")


migrate_db()


# ================= DB 함수 =================
def save_user(chat_id):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (chat_id)
            VALUES (%s)
            ON CONFLICT (chat_id) DO NOTHING
        """, (chat_id,))


def set_user_language(chat_id, language):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE users
            SET language = %s
            WHERE chat_id = %s
        """, (language, chat_id))


def get_user_language(chat_id):
    with conn.cursor() as cur:
        cur.execute("SELECT language FROM users WHERE chat_id=%s", (chat_id,))
        row = cur.fetchone()
        return row[0] if row else "EN"


def get_user_count():
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]


# ================= Webhook =================
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Bot is running"

    update = request.get_json()
    if not update:
        return "ok"

    # ---------- 메시지 ----------
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            save_user(chat_id)

            keyboard = {
                "inline_keyboard": [
                    [{"text": "🇬🇧 EN", "callback_data": "lang_EN"}],
                    [{"text": "🇫🇷 FR", "callback_data": "lang_FR"}],
                    [{"text": "🇨🇳 ZH", "callback_data": "lang_ZH"}],
                    [{"text": "🇸🇦 AR", "callback_data": "lang_AR"}],
                    [{"text": "🇪🇸 ES", "callback_data": "lang_ES"}]
                ]
            }

            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Please select your language",
                "reply_markup": keyboard
            })

        elif text == "/users" and chat_id == ADMIN_ID:
            count = get_user_count()
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"👥 Total users: {count}"
            })

    # ---------- 버튼 ----------
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["from"]["id"]
        data = cq["data"]

        # Telegram 로딩 멈추기
        requests.post(f"{API_URL}/answerCallbackQuery", json={
            "callback_query_id": cq["id"]
        })

        if data.startswith("lang_"):
            lang = data.split("_")[1]
            set_user_language(chat_id, lang)

            requests.post(f"{API_URL}/sendVideo", json={
                "chat_id": chat_id,
                "video": VIDEO_URL,
                "caption": CAPTIONS.get(lang, CAPTIONS["EN"])
            })

            payment_keyboard = {
                "inline_keyboard": [
                    [{"text": "💸 PayPal", "url": "https://www.paypal.com/paypalme/minwookim384/20usd"}],
                    [{"text": "💳 Stripe", "url": "https://buy.stripe.com/bJe8wR1oO1nq3sN7Y41ck00"}],
                    [{"text": "🪙 CRYPTO USDT(TRON)", "callback_data": "crypto"}],
                    [{"text": "❓ Proof here", "url": "https://t.me/MBRYPIE"}]
                ]
            }

            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "💡 After payment, please send proof",
                "reply_markup": payment_keyboard
            })

        elif data == "crypto":
            requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id,
                "photo": CRYPTO_QR,
                "caption": f"USDT (TRON)\n\n{CRYPTO_ADDRESS}"
            })

    return "ok"


# ================= Render 실행 =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
