import psycopg2
import urllib.parse as up
import os

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

with conn.cursor() as cur:
    cur.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'EN'
    """)
    print("✅ language 컬럼 추가 완료")

conn.close()
