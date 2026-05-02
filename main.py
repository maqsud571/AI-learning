import os
from datetime import datetime

from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from Database.database import SessionLocal, engine, Base
from models import Car

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


from prompts import SQL_PROMPT, ANALYTICS_PROMPT, FORMATTER_PROMPT

load_dotenv()

app = FastAPI(title="Qalesan !")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.5
)

async def get_db():
    async with SessionLocal() as s:
        yield s

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class ChatRequest(BaseModel):
    message: str

class AskRequest(BaseModel):
    question: str

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ai(prompt: str):
    try:
        res = llm.invoke([
            SystemMessage(content="Sen qisqa, aniq assistant san."),
            HumanMessage(content=prompt)
        ])
        return res.content.strip()
    except Exception as e:
        return str(e)

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


def is_safe_query(query: str):
    forbidden = ["drop", "delete", "truncate", "alter"]
    q = query.lower()
    return not any(x in q for x in forbidden)


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


def format_answer(question, sql, result):
    prompt = FORMATTER_PROMPT.format(
        question=question,
        sql=sql,
        result=result
    )
    return ai(prompt)


@app.get("/")
def home():
    return {"message": "AI DB API 🚗🤖", "time": now()}

class CarCreate(BaseModel):
    brand: str
    model: str
    color: str
    year: int
    quantity: int

@app.post("/cars")
async def create_car(car: CarCreate, db: AsyncSession = Depends(get_db)):

    new_car = Car(**car.model_dump())

    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)

    return {
        "message": "Car successfully created 🚗",
        "car": {
            "id": new_car.id,
            "brand": new_car.brand,
            "model": new_car.model,
            "color": new_car.color,
            "year": new_car.year,
            "quantity": new_car.quantity
        },
        "time": now()
    }

@app.get("/cars")
async def get_cars(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Car))
    cars = result.scalars().all()

    return {
        "count": len(cars),
        "cars": [
            {
                "id": c.id,
                "brand": c.brand,
                "model": c.model,
                "color": c.color,
                "year": c.year,
                "quantity": c.quantity
            }
            for c in cars
        ],
        "time": now()
    }


# ask/ api nmalar qiladi
# schema ni o'qiydi 
# AI SQL generatsiya qiladi 
# SQL clean qiladi 
# xavfsizlik tekshiruvi qiladi 
# DB execute qiladi 
# natijani AI gapga aylantiradi
@app.post("/ask")
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):

    schema = await get_schema(db)

    if not schema:
        return {"error": "Database bo'sh"}

    # SQL generate qvoti
    sql_prompt = SQL_PROMPT.format(
        schema=schema,
        question=req.question
    )

    ai_sql = ai(sql_prompt)

    
    ai_sql = ai_sql.replace("```sql", "").replace("```", "").strip()

    for k in ["select", "insert", "update"]:
        if k in ai_sql.lower():
            ai_sql = ai_sql[ai_sql.lower().index(k):]
            break

    if not is_safe_query(ai_sql):
        return {"error": "Unsafe query", "sql": ai_sql}

    result = await execute_query(db, ai_sql)
    answer = format_answer(req.question, ai_sql, result)

    return {
        "answer": answer,
        "sql": ai_sql,
        "result": result,
        "time": now()
    }

# ask-simple/ esa har qanday savolga javob beradi, SQL ni ham javobning ichida yozadi, 
@app.post("/ask-simple")
async def ask_simple(req: AskRequest, db: AsyncSession = Depends(get_db)):

    total = (await db.execute(select(func.count(Car.id)))).scalar()
    brands = (await db.execute(select(func.distinct(Car.brand)))).scalars().all()
    colors = (await db.execute(select(func.distinct(Car.color)))).scalars().all()
    years = (await db.execute(select(func.distinct(Car.year)))).scalars().all()
    quantities = (await db.execute(select(func.distinct(Car.quantity)))).scalars().all()

    prompt = ANALYTICS_PROMPT.format(
        total=total,
        brands=brands,
        colors=colors,
        years=years,
        quantities=quantities,
        question=req.question
    )

    return {
        "answer": ai(prompt),
        "time": now()
    }
