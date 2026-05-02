import os
from datetime import datetime

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from Database.database import SessionLocal, engine, Base

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from prompts.sql import SQL_PROMPT
from prompts.router import ROUTER_PROMPT
from prompts.formatter import FORMATTER_PROMPT

load_dotenv()

app = FastAPI(title="AI Database Agent")


# ================= LLM =================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)


# ================= VAQT =================
def now():
    """
    📅 Hozirgi vaqtni qaytaradi
    API response uchun ishlatiladi
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


"""
    Bu funksiya:
    - prompt yuboradi
    - Gemini javobini oladi
    - xatoni ushlaydi
"""
def ai(prompt: str):

    try:
        res = llm.invoke([
            SystemMessage(content="Siz yordamchi AI siz."),
            HumanMessage(content=prompt)
        ])
        return res.content.strip()

    except Exception as e:
        return f"AI ERROR: {str(e)}"

# database
async def get_db():
    """
    🔌 DB bilan ulanish (session)

    FastAPI dependency uchun ishlatiladi
    """
    async with SessionLocal() as s:
        yield s


# ================= STARTUP =================
@app.on_event("startup")
async def startup():
    """
    🚀 Server ishga tushganda:

    - DB tablelarni yaratadi (models.py asosida)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ================= SCHEMA OLISH =================
async def get_schema(db: AsyncSession):
    """
    🧠 Database strukturasini olish

    Natija:
    {
        table: [columns]
    }

    Bu AI ga DB ni tushuntirish uchun kerak
    """
    query = text("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    result = await db.execute(query)
    rows = result.fetchall()

    schema = {}

    for table, column, dtype in rows:
        schema.setdefault(table, []).append(column)

    return schema


# ================= DDL O‘QISH =================
def load_ddl():
    """
    📄 ddl.sql faylini o‘qish

    AI ga qo‘shimcha context beradi
    """
    try:
        with open("Database/ddl.sql", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


# ================= SCHEMA + DDL =================
async def get_full_schema(db: AsyncSession):
    """
    🧠 AI uchun to‘liq schema:

    - real DB schema
    - ddl.sql 
    """
    return {
        "db_schema": await get_schema(db),
        "ddl": load_ddl()
    }


# ================= SQL XAVFSIZLIK =================
def is_safe_query(sql: str):

    bad_words = ["drop", "delete", "truncate", "alter"]
    sql = sql.lower()
    return not any(word in sql for word in bad_words)


# ================= SQL TOZALASH =================
def normalize_sql(sql: str):
    """
    🧹 AI yozgan SQL ni tozalaydi

    - ```sql ni olib tashlaydi
    """
    return sql.replace("```sql", "").replace("```", "").strip()


# ================= SQL EXECUTE =================
async def execute_query(db: AsyncSession, sql: str):
    """
    🧾 SQL ni database da ishlatadi

    - SELECT → data qaytaradi
    - boshqa → commit qiladi
    """
    try:
        result = await db.execute(text(sql))

        if sql.lower().startswith("select"):
            rows = result.fetchall()
            return [dict(r._mapping) for r in rows]

        await db.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}


# ================= REQUEST MODEL =================
class AskRequest(BaseModel):
    """
    📩 User request modeli
    """
    question: str


# ================= ROUTER =================
def classify_question(question: str, schema: dict):
    """
    🧭 Savolni 3 ga ajratadi:

    - db     → database kerak
    - chat   → oddiy javob
    - reject → ruxsat yo‘q
    """
    prompt = ROUTER_PROMPT.format(
        question=question,
        schema=schema
    )

    res = ai(prompt).lower()

    if res == "db":
        return "db"

    if res == "chat":
        return "chat"

    return "reject"


# ================= SQL GENERATOR =================
def generate_sql(question: str, schema: dict):
    """
    🧠 Matnni SQL ga aylantiradi
    """
    prompt = SQL_PROMPT.format(
        question=question,
        schema=schema
    )

    return ai(prompt)


# ================= FORMATTER =================
def format_answer(question, sql, result):
    """
    🎯 DB result ni userga tushunarli qilib beradi
    """
    prompt = FORMATTER_PROMPT.format(
        question=question,
        sql=sql,
        result=result
    )

    return ai(prompt)


# ================= MAIN API =================
@app.post("/ask")
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):

    # 1. schema olish
    schema = await get_full_schema(db)

    # 2. savolni tekshirish
    intent = classify_question(req.question, schema)

    # ================= REJECT =================
    if intent == "reject":
        return {
            "type": "blocked",
            "answer": "Bu system faqat database va oddiy savollarga javob beradi",
            "time": now()
        }

    # ================= CHAT =================
    if intent == "chat":
        return {
            "type": "chat",
            "answer": ai(req.question),
            "time": now()
        }

    # ================= DB =================
    if intent == "db":

        # SQL yaratish
        sql = generate_sql(req.question, schema)

        # tozalash
        sql = normalize_sql(sql)

        # faqat SELECT
        if "select" in sql.lower():
            sql = sql[sql.lower().index("select"):]

        # xavfsizlik
        if not is_safe_query(sql):
            return {
                "type": "blocked",
                "error": "Unsafe SQL",
                "sql": sql
            }

        # execute
        result = await execute_query(db, sql)

        # format
        answer = format_answer(req.question, sql, result)

        return {
            "type": "db",
            "answer": answer,
            "sql": sql,
            "result": result,
            "time": now()
        }


# ================= HOME =================
@app.get("/")
def home():
    """
    🏠 System status
    """
    return {
        "status": "running",
        "system": "AI Database Agent"
    }