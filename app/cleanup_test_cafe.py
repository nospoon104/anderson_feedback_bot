import asyncio

from sqlalchemy import delete, select, update

from app.db.models import Cafe, Survey, User
from app.db.session import AsyncSessionLocal


TEST_CAFE_CODE = "cafe_center"


async def cleanup_test_cafe() -> None:
    confirm = input(
        f"Удалить тестовое кафе с code='{TEST_CAFE_CODE}'? Напиши YES: "
    ).strip()

    if confirm != "YES":
        print("Отмена.")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Cafe).where(Cafe.code == TEST_CAFE_CODE))
        cafe = result.scalar_one_or_none()

        if cafe is None:
            print("Тестовое кафе не найдено.")
            return

        cafe_id = cafe.id

        await session.execute(delete(Survey).where(Survey.cafe_id == cafe_id))

        await session.execute(
            update(User).where(User.cafe_id == cafe_id).values(cafe_id=None)
        )

        await session.execute(delete(Cafe).where(Cafe.id == cafe_id))

        await session.commit()

        print(
            f"Тестовое кафе удалено: id={cafe_id}, code={TEST_CAFE_CODE}, name={cafe.name}"
        )


if __name__ == "__main__":
    asyncio.run(cleanup_test_cafe())
