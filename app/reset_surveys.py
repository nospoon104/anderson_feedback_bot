import asyncio

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


async def reset_surveys() -> None:
    confirm = input("Удалить ВСЕ анкеты из таблицы surveys? Напиши YES: ").strip()

    if confirm != "YES":
        print("Отмена.")
        return

    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE surveys RESTART IDENTITY CASCADE"))
        await session.commit()

    print("Таблица surveys очищена. ID сброшены.")


if __name__ == "__main__":
    asyncio.run(reset_surveys())
