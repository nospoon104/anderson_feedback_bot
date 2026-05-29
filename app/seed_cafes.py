import asyncio

from app.db.repositories.cafe_repository import CafeRepository
from app.db.session import AsyncSessionLocal
from app.schemas.cafe import CafeCreateSchema


CAFES_TO_SEED = [
    {
        "name": "Андерсон Таганская",
        "code": "cafe_taganka",
        "address": "ул. Центральная, 1",
    },
]


async def seed_cafes() -> None:
    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)

        for cafe_data in CAFES_TO_SEED:
            existing_cafe = await cafe_repository.get_by_code(cafe_data["code"])

            if existing_cafe is not None:
                print(
                    f"Уже существует: "
                    f"id={existing_cafe.id}, "
                    f"code={existing_cafe.code}, "
                    f"name={existing_cafe.name}"
                )
                continue

            cafe = await cafe_repository.create(
                CafeCreateSchema(
                    name=cafe_data["name"],
                    code=cafe_data["code"],
                    address=cafe_data["address"],
                )
            )

            print(
                f"Создано кафе: "
                f"id={cafe.id}, "
                f"code={cafe.code}, "
                f"name={cafe.name}"
            )


if __name__ == "__main__":
    asyncio.run(seed_cafes())
