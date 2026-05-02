import os
from datetime import datetime

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from Database.database import SessionLocal, engine, Base
from models import Car

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from prompts import SQL_PROMPT, FORMATTER_PROMPT

load_dotenv()

app = FastAPI(title="Cars AI Agent 🚗🤖")

# ================= AI =================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ai(prompt: str):
    try:
        res = llm.invoke([
            SystemMessage(content="Sen aqlli assistantsan. Cars DB va chat bilan ishlaysan."),
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
    sql = sql.replace(" = '", " = LOWER('")  
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

# ================= ROUTER (DB / CHAT / REJECT) =================
def classify_question(question: str, schema: dict):
    prompt = f"""
Sen AI routerisan.

SCHEMA:
{schema}

Vazifa:
Savolni 3 turga ajrat:

1. db → cars database savollari
2. chat → oddiy suhbat, salom, fikr, analiz
3. reject → boshqa mavzular (weather, hacking, politics)

QOIDALAR:
- Cars bo‘lsa → db
- Salom / gaplashish / fikr → chat
- Boshqa hamma narsa → reject

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

# ================= FORMAT =================
def format_answer(question, sql, result):
    prompt = FORMATTER_PROMPT.format(
        question=question,
        sql=sql,
        result=result
    )
    return ai(prompt)

# ================= MAIN ENDPOINT =================
@app.post("/ask")
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):

    schema = await get_schema(db)

    if not schema:
        return {"error": "Database bo'sh"}

    # 🧠 ROUTER
    intent = classify_question(req.question, schema)

# /////////////////////////////////
    # ================= REJECT =================
    if intent == "reject":
        return {
            "type": "blocked",
            "answer": "❌ Men faqat Cars DB va umumiy suhbat uchun ishlayman.",
            "time": now()
        }

    # ================= CHAT MODE =================
    if intent == "chat":
        return {
            "type": "chat",
            "answer": ai(req.question),
            "time": now()
        }

    # ================= DB MODE =================
    if intent == "db":

        sql_prompt = SQL_PROMPT.format(
            schema=schema,
            question=req.question
        )

        ai_sql = ai(sql_prompt)
        ai_sql = normalize_sql(ai_sql)
# ///////////////////////////////
        # safety trim
        for k in ["select", "insert", "update"]:
            if k in ai_sql.lower():
                ai_sql = ai_sql[ai_sql.lower().index(k):]
                break

        if not is_safe_query(ai_sql):
            return {"error": "Unsafe query", "sql": ai_sql}

        result = await execute_query(db, ai_sql)
        answer = format_answer(req.question, ai_sql, result)

        return {
            "type": "cars_db",
            "answer": answer,
            "sql": ai_sql,
            "result": result,
            "time": now()
        }

# ================= HOME =================
@app.get("/")
def home():
    return {
        "message": "Cars AI Agent 🚗🤖",
        "modes": {
            "db": "Cars database queries",
            "chat": "General conversation",
            "reject": "Blocked topics"
        },
        "features": [
            "Case-insensitive search (mers = MERS)",
            "AI router (db/chat/reject)",
            "Safe SQL execution",
            "Auto SQL generation"
        ],
        "time": now()
    }