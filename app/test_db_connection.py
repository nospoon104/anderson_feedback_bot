import asyncio

from sqlalchemy import text

from app.db.session import engine


async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB connection OK:", result.scalar())


if __name__ == "__main__":
    asyncio.run(test_connection())
