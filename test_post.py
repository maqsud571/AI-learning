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

load_dotenv()

app = FastAPI(title="Multi-Table AI Agent 🤖")

# ================= AI =================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY"),
#     temperature=0.3
# )

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ai(prompt: str):
    try:
        res = llm.invoke([
            SystemMessage(content="""
Sen kuchli AI assistantsan.

Siz quyidagi DB bilan ishlaysiz:
- cars (mashinalar)
- books (kitoblar)
- stationery (kanstovar)
- construction (qurilish mollari)

Sen user savolini tushunib:
- to‘g‘ri table tanlaysan
- to‘g‘ri SQL yozasan
- yoki oddiy javob berasan
"""),
            HumanMessage(content=prompt)
        ])
        return res.content.strip()
    except Exception as e:
        return str(e)

# ================= DB =================
async def get_db():
    async with SessionLocal() as s:
        yield s

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ================= SCHEMA =================
async def get_schema(db: AsyncSession):
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
        schema.setdefault(table, []).append(f"{column} ({dtype})")

    return schema

# ================= SAFETY =================
def is_safe_query(query: str):
    forbidden = ["drop", "delete", "truncate", "alter"]
    q = query.lower()
    return not any(x in q for x in forbidden)

def normalize_sql(sql: str):
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

async def execute_query(db: AsyncSession, sql_query: str):
    try:
        result = await db.execute(text(sql_query))

        if sql_query.lower().startswith("select"):
            rows = result.fetchall()
            return [dict(r._mapping) for r in rows]

        await db.commit()
        return {"status": "success"}

    except Exception as e:
        return {"error": str(e)}

# ================= REQUEST =================
class AskRequest(BaseModel):
    question: str

# ================= ROUTER =================
def classify_question(question: str, schema: dict):
    prompt = f"""
Sen AI routerisan.

SCHEMA:
{schema}

Vazifa:
Savolni 3 turga ajrat:

1. db → database savollari (cars, books, stationery, construction)
2. chat → oddiy suhbat
3. reject → boshqa mavzular

QOIDALAR:
- Mashina, kitob, ruchka, sement → db
- Salomlashish → chat
- Weather, hacking, siyosat → reject

Faqat bitta so‘z qaytar:
db / chat / reject

Savol:
{question}
"""
    res = ai(prompt).lower()

    if "db" in res:
        return "db"
    if "chat" in res:
        return "chat"
    return "reject"

# ================= SQL GENERATOR =================
def generate_sql(question: str, schema: dict):
    prompt = f"""
Sen PostgreSQL expertisan.

SCHEMA:
{schema}

QOIDALAR:
- Faqat SELECT yoz
- To‘g‘ri table tanla:
  cars / books / stationery / construction
- LIKE ishlat (case-insensitive)
- LIMIT 10 qo‘sh

Savol:
{question}

Faqat SQL qaytar.
"""
    return ai(prompt)

# ================= FORMAT =================
def format_answer(question, sql, result):
    prompt = f"""
User savoli: {question}

SQL:
{sql}

Natija:
{result}

Oddiy, tushunarli javob qilib ber.
"""
    return ai(prompt)

# ================= MAIN =================
@app.post("/ask")
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):

    schema = await get_schema(db)

    if not schema:
        return {"error": "Database bo'sh"}

    intent = classify_question(req.question, schema)

    # ================= REJECT =================
    if intent == "reject":
        return {
            "type": "blocked",
            "answer": "❌ Bu mavzuga javob bermayman",
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

        ai_sql = generate_sql(req.question, schema)
        ai_sql = normalize_sql(ai_sql)

        # trim
        if "select" in ai_sql.lower():
            ai_sql = ai_sql[ai_sql.lower().index("select"):]

        if not is_safe_query(ai_sql):
            return {"error": "Unsafe query", "sql": ai_sql}

        result = await execute_query(db, ai_sql)
        answer = format_answer(req.question, ai_sql, result)

        return {
            "type": "multi_db",
            "answer": answer,
            "sql": ai_sql,
            "result": result,
            "time": now()
        }

# ================= HOME =================
@app.get("/")
def home():
    return {
        "message": "Multi-Table AI Agent 🤖",
        "tables": ["cars", "books", "stationery", "construction"],
        "features": [
            "AI table selection",
            "Auto SQL generation",
            "Safe queries",
            "Chat + DB hybrid"
        ],
        "time": now()
    }