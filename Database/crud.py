from sqlalchemy import text

# 📊 schema olish
async def get_schema(db):
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
        if table not in schema:
            schema[table] = []
        schema[table].append(f"{column} ({dtype})")

    return schema


# ⚡ query execute qilish
async def execute_query(db, sql_query: str):
    try:
        result = await db.execute(text(sql_query))

        if sql_query.strip().lower().startswith("select"):
            return result.fetchall()

        await db.commit()
        return {"status": "success"}

    except Exception as e:
        return {"error": str(e)}