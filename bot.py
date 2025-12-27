from flask import Flask, request
import requests
import os
import psycopg2
import urllib.parse as up

app = Flask(__name__)

# ===== 기본 설정 =====
TOKEN = os.environ.get("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

VIDEO_URL = "https://files.catbox.moe/dt49t2.mp4"

# ===== 캡션 (줄마다 빈 줄 추가) =====
CAPTIONS = {
    "EN": """
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
""",
    "FR": """
──────────────────────────────

Bienvenue dans la Collection Privée

──────────────────────────────

• Contenu sélectionné de haute qualité uniquement.

• Vidéos Premium ★nlyFans

• DÉCEMBRE 2025 : ★ ACTIF ★

──────────────────────────────

★ Prix : 20$

★ ACCÈS INSTANTANÉ ★

──────────────────────────────
""",
    "ZH": """
──────────────────────────────

私人收藏欢迎您

──────────────────────────────

• 仅高质量精选内容

• 高级 ★nlyFans 视频

• 2025年12月：★ 活跃 ★

──────────────────────────────

★ 价格：$20

★ 即刻访问 ★

──────────────────────────────
""",
    "AR": """
──────────────────────────────

مرحبًا بك في المجموعة الخاصة

──────────────────────────────

• محتوى مختار عالي الجودة فقط

• فيديوهات ★nlyFans المميزة

• ديسمبر 2025: ★ نشط ★

──────────────────────────────

★ السعر: 20$

★ الوصول الفوري ★

──────────────────────────────
""",
    "ES": """
──────────────────────────────

Bienvenido a la Colección Privada

──────────────────────────────

• Solo contenido seleccionado de alta calidad

• Videos Premium ★nlyFans

• DICIEMBRE 2025: ★ ACTIVO ★

──────────────────────────────

★ Precio: $20

★ ACCESO INSTANTÁNEO ★

──────────────────────────────
"""
}

ADMIN_ID = 5619516265

CRYPTO_QR = "https://files.catbox.moe/fkxh5l.png"
CRYPTO_ADDRESS = "TERhALhVLZRqnS3mZGhE1XgxyLnKHfgBLi"

# ===== Render Postgres 연결 =====
DATABASE_URL = os.environ["DATABASE_URL"]

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

# ===== DB 함수 =====
def save_user(chat_id):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY,
                language TEXT DEFAULT 'EN'
            )
        """)
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
        result = cur.fetchone()
        return result[0] if result else "EN"

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
    if not update:
        return "ok"

    message = update.get("message")
    callback_query = update.get("callback_query")
    
    # ===== 일반 메시지 처리 =====
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            save_user(chat_id)

            # 언어 선택 버튼
            lang_keyboard = {
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
                "reply_markup": lang_keyboard
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

    # ===== 버튼 클릭 처리 =====
    elif callback_query:
        chat_id = callback_query["from"]["id"]
        data = callback_query["data"]

        # ✅ 버튼 클릭 처리 완료 응답
        callback_id = callback_query["id"]
        requests.post(f"{API_URL}/answerCallbackQuery", json={
            "callback_query_id": callback_id
        })

        # 언어 선택
        if data.startswith("lang_"):
            language = data.split("_")[1]
            set_user_language(chat_id, language)

            # 안내 메시지
            messages = {
                "EN": "✅ Language set to English.",
                "FR": "✅ Langue définie sur le français.",
                "ZH": "✅ 语言已设置为中文。",
                "AR": "✅ تم تعيين اللغة إلى العربية.",
                "ES": "✅ Idioma configurado a Español."
            }
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": messages.get(language, messages["EN"])
            })

            # 선택 후 영상 전송
            requests.post(f"{API_URL}/sendVideo", json={
                "chat_id": chat_id,
                "video": VIDEO_URL,
                "caption": CAPTIONS.get(language, CAPTIONS["EN"])
            })

            # 결제 버튼
            payment_texts = {
                "EN": "💡 After payment, please send me a proof!",
                "FR": "💡 Après le paiement, veuillez m'envoyer une preuve !",
                "ZH": "💡 付款后，请发送付款凭证！",
                "AR": "💡 بعد الدفع، يرجى إرسال الإثبات!",
                "ES": "💡 Después del pago, por favor envíeme una prueba!"
            }

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
                "text": payment_texts.get(language, payment_texts["EN"]),
                "reply_markup": payment_keyboard
            })

        # CRYPTO 버튼
        elif data == "crypto":
            requests.post(f"{API_URL}/sendPhoto", json={
                "chat_id": chat_id,
                "photo": CRYPTO_QR,
                "caption": f"💡 CRYPTO USDT(TRON) Payment\n\nWallet Address:\n{CRYPTO_ADDRESS}"
            })

            proof_keyboard = {
                "inline_keyboard": [
                    [{"text": "❓ Proof here", "url": "https://t.me/MBRYPIE"}]
                ]
            }
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "💡 After payment, please send me a proof!",
                "reply_markup": proof_keyboard
            })

    return "ok"

# ===== Render 실행 =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

