import asyncio

from app.db.repositories.cafe_repository import CafeRepository
from app.db.session import AsyncSessionLocal


async def check_cafes() -> None:
    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        cafes = await cafe_repository.list_all()

        if not cafes:
            print("Кафе в базе не найдены.")
            return

        print("CAFES:")
        for cafe in cafes:
            print(
                f"id={cafe.id}, "
                f"name={cafe.name}, "
                f"code={cafe.code}, "
                f"address={cafe.address}, "
                f"is_active={cafe.is_active}"
            )


if __name__ == "__main__":
    asyncio.run(check_cafes())
