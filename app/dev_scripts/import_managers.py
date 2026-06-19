import asyncio

from app.core.constants import ROLE_MANAGER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateSchema


MANAGERS_TO_IMPORT = [
    {
        "full_name": "Куликова Ирина",
        "telegram_id": 478966118,
        "cafe_code": "cafe_bratislavskaya",
    },
    {
        "full_name": "Мальцева Анастасия",
        "telegram_id": 530304483,
        "cafe_code": "cafe_bratislavskaya",
    },
    {
        "full_name": "Козырева Ирина",
        "telegram_id": 830245665,
        "cafe_code": "cafe_bratislavskaya",
    },
    {
        "full_name": "Никифорова Анна",
        "telegram_id": 927009099,
        "cafe_code": "cafe_gagarinskiy",
    },
    {
        "full_name": "Боровикова Наталья",
        "telegram_id": 1040849800,
        "cafe_code": "cafe_gagarinskiy",
    },
    {
        "full_name": "Кожевина Дарья",
        "telegram_id": 602602994,
        "cafe_code": "cafe_gagarinskiy",
    },
    {
        "full_name": "Светличный Максим",
        "telegram_id": 6567617290,
        "cafe_code": "cafe_gilyarovskogo",
    },
    {
        "full_name": "Полуян Арина",
        "telegram_id": 1072188121,
        "cafe_code": "cafe_gilyarovskogo",
    },
    {
        "full_name": "Малыхин Влад",
        "telegram_id": 519898536,
        "cafe_code": "cafe_gilyarovskogo",
    },
    {
        "full_name": "Золоев Артем",
        "telegram_id": 5961731846,
        "cafe_code": "cafe_gilyarovskogo",
    },
    {
        "full_name": "Панина Алия",
        "telegram_id": 717833822,
        "cafe_code": "cafe_domodedovo",
    },
    {
        "full_name": "Ярохно Елена",
        "telegram_id": 541962740,
        "cafe_code": "cafe_domodedovo",
    },
    {
        "full_name": "Мартыненкова Ольга",
        "telegram_id": 956632185,
        "cafe_code": "cafe_kaskad",
    },
    {
        "full_name": "Мартыненко Екатерина",
        "telegram_id": 1350681132,
        "cafe_code": "cafe_kaskad",
    },
    {
        "full_name": "Минхаеров Рустем",
        "telegram_id": 1657518592,
        "cafe_code": "cafe_kaskad",
    },
    {
        "full_name": "Пальчикова Алина",
        "telegram_id": 747045517,
        "cafe_code": "cafe_kuskovskaya",
    },
    {
        "full_name": "Афанаскин Максим",
        "telegram_id": 1050639425,
        "cafe_code": "cafe_kuskovskaya",
    },
    {
        "full_name": "Кузнецова Валерия",
        "telegram_id": 1644733957,
        "cafe_code": "cafe_kuskovskaya",
    },
    {
        "full_name": "Мартыненкова Ольга",
        "telegram_id": 956632185,
        "cafe_code": "cafe_obrucheva",
    },
    {
        "full_name": "Сергиенко Олеся",
        "telegram_id": 421063156,
        "cafe_code": "cafe_obrucheva",
    },
    {
        "full_name": "Голова Кристина",
        "telegram_id": 8193111870,
        "cafe_code": "cafe_obrucheva",
    },
    {
        "full_name": "Дудкина Екатерина",
        "telegram_id": 567637066,
        "cafe_code": "cafe_obrucheva",
    },
    {
        "full_name": "Шидловский Дмитрий",
        "telegram_id": 97874985,
        "cafe_code": "cafe_sokol",
    },
    {"full_name": "Власова Ольга", "telegram_id": 733410741, "cafe_code": "cafe_sokol"},
    {
        "full_name": "Калашников Александр",
        "telegram_id": 897147169,
        "cafe_code": "cafe_sokol",
    },
    {
        "full_name": "Чечулина Екатерина",
        "telegram_id": 1267956927,
        "cafe_code": "cafe_sokol",
    },
    {
        "full_name": "Емельянова Елена",
        "telegram_id": 207584917,
        "cafe_code": "cafe_taganskaya_36",
    },
    {
        "full_name": "Портянов Максим",
        "telegram_id": 1077841282,
        "cafe_code": "cafe_taganskaya_36",
    },
    {
        "full_name": "Моисеева Кристина",
        "telegram_id": 819427474,
        "cafe_code": "cafe_tsaritsyno",
    },
    {
        "full_name": "Емелькина Яна",
        "telegram_id": 837929393,
        "cafe_code": "cafe_tsaritsyno",
    },
    {
        "full_name": "Реулова Дарья",
        "telegram_id": 727806797,
        "cafe_code": "cafe_tsaritsyno",
    },
    {
        "full_name": "Степанова Алёна",
        "telegram_id": 454676035,
        "cafe_code": "cafe_tsaritsyno",
    },
    {
        "full_name": "Нематова Азиза",
        "telegram_id": 345095251,
        "cafe_code": "cafe_tsaritsyno",
    },
    {
        "full_name": "Моисеева Кристина",
        "telegram_id": 819427474,
        "cafe_code": "cafe_festival",
    },
    {
        "full_name": "Юрасова Софья",
        "telegram_id": 829015798,
        "cafe_code": "cafe_festival",
    },
    {
        "full_name": "Генералова Нина",
        "telegram_id": 1142337816,
        "cafe_code": "cafe_festival",
    },
]


async def import_managers() -> None:
    created_count = 0
    updated_count = 0
    skipped_count = 0

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        cafe_repository = CafeRepository(session)

        for item in MANAGERS_TO_IMPORT:
            full_name = item["full_name"].strip()
            telegram_id = item["telegram_id"]
            cafe_code = item["cafe_code"].strip()

            cafe = await cafe_repository.get_by_code(cafe_code)
            if cafe is None:
                print(
                    f"[SKIP] Кафе не найдено: "
                    f"code={cafe_code}, user={full_name}, telegram_id={telegram_id}"
                )
                skipped_count += 1
                continue

            existing_user = await user_repository.get_by_telegram_id(telegram_id)

            if existing_user is not None:
                existing_user.full_name = full_name
                existing_user.role = ROLE_MANAGER
                existing_user.cafe_id = cafe.id

                await session.commit()
                await session.refresh(existing_user)

                print(
                    f"[UPDATED] "
                    f"id={existing_user.id}, "
                    f"telegram_id={existing_user.telegram_id}, "
                    f"name={existing_user.full_name}, "
                    f"cafe_id={existing_user.cafe_id}, "
                    f"cafe_code={cafe.code}"
                )
                updated_count += 1
                continue

            user = await user_repository.create(
                UserCreateSchema(
                    telegram_id=telegram_id,
                    full_name=full_name,
                    role=ROLE_MANAGER,
                    cafe_id=cafe.id,
                )
            )

            print(
                f"[CREATED] "
                f"id={user.id}, "
                f"telegram_id={user.telegram_id}, "
                f"name={user.full_name}, "
                f"cafe_id={user.cafe_id}, "
                f"cafe_code={cafe.code}"
            )
            created_count += 1

    print()
    print("Импорт завершён:")
    print(f"  created={created_count}")
    print(f"  updated={updated_count}")
    print(f"  skipped={skipped_count}")


if __name__ == "__main__":
    asyncio.run(import_managers())
