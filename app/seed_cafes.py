import asyncio

from app.db.repositories.cafe_repository import CafeRepository
from app.db.session import AsyncSessionLocal
from app.schemas.cafe import CafeCreateSchema


CAFES_TO_SEED = [
    {
        "name": "АндерСон Таганская 36",
        "code": "cafe_taganskaya_36",
        "address": "-",
    },
    {
        "name": "АндерСон Авеню",
        "code": "cafe_avenyu",
        "address": "-",
    },
    {
        "name": "АндерСон Братиславская",
        "code": "cafe_bratislavskaya",
        "address": "-",
    },
    {
        "name": "АндерСон Бутово",
        "code": "cafe_butovo",
        "address": "-",
    },
    {
        "name": "АндерСон Гагаринский",
        "code": "cafe_gagarinskiy",
        "address": "-",
    },
    {
        "name": "АндерСон Гиляровского",
        "code": "cafe_gilyarovskogo",
        "address": "-",
    },
    {
        "name": "АндерСон Домодедово",
        "code": "cafe_domodedovo",
        "address": "-",
    },
    {
        "name": "АндерСон Кусковская",
        "code": "cafe_kuskovskaya",
        "address": "-",
    },
    {
        "name": "АндерСон Каскад",
        "code": "cafe_kaskad",
        "address": "-",
    },
    {
        "name": "АндерСон Медведково",
        "code": "cafe_medvedkovo",
        "address": "-",
    },
    {
        "name": "АндерСон Мичуринский",
        "code": "cafe_michurinskiy",
        "address": "-",
    },
    {
        "name": "АндерСон Обручева",
        "code": "cafe_obrucheva",
        "address": "-",
    },
    {
        "name": "АндерСон Островитянова",
        "code": "cafe_ostrovityanova",
        "address": "-",
    },
    {
        "name": "АндерСон Сокол",
        "code": "cafe_sokol",
        "address": "-",
    },
    {
        "name": "АндерСон Царицыно",
        "code": "cafe_tsaritsyno",
        "address": "-",
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
