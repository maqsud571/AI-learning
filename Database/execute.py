import asyncio
from sqlalchemy import text
from Database.database import engine

DDL_PATH = "Database/ddl.sql"


def load_ddl():
    """📄 ddl.sql faylni o‘qiydi"""
    with open(DDL_PATH, "r", encoding="utf-8") as f:
        return f.read()


async def run_ddl():
    """
    🧠 ddl.sql ni PostgreSQL ga apply qiladi
    - tablelar yaratadi
    """
    ddl = load_ddl()

    async with engine.begin() as conn:
        # split by ; (har bir SQL statement)
        for statement in ddl.split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt))

    print("✅ DDL executed successfully")


# async def seed_data():
#     """
#     🌱 TEST DATA qo‘shish
#     - development uchun sample data
#     """

#     async with engine.begin() as conn:

#         # cars table
#         await conn.execute(text("""
#             INSERT INTO cars (name, price, year)
#             VALUES 
#             ('BMW M5', 90000, 2022),
#             ('Tesla Model S', 110000, 2023);
#         """))

#         # books table
#         await conn.execute(text("""
#             INSERT INTO books (title, author, price)
#             VALUES 
#             ('Clean Code', 'Robert Martin', 35),
#             ('Deep Work', 'Cal Newport', 20);
#         """))

#     print("🌱 Seed data inserted")


async def reset_db():
    """
    ⚠️ DB ni tozalab qayta build qiladi
    - dev mode uchun
    """

    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))

    print("🧨 Database reset done")


async def init():
    """
    🚀 FULL INIT PIPELINE
    - reset → ddl → seed
    """

    print("🚀 Starting DB initialization...")

    await reset_db()
    await run_ddl()
    # await seed_data()

    print("🎉 DB is ready!")


# ---------------- RUN DIRECTLY ----------------
if __name__ == "__main__":
    asyncio.run(init())