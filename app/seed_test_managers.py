import asyncio
from sqlalchemy import select

from app.core.constants import ROLE_MANAGER
from app.db.models import User
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateSchema


TEST_MANAGER_NAME_PREFIX = "test_manager"
TEST_TELEGRAM_ID_BASE = 900_000_000_000


async def manager_exists_for_cafe(session, cafe_id: int) -> bool:
    result = await session.execute(
        select(User).where(User.role == ROLE_MANAGER).where(User.cafe_id == cafe_id)
    )
    user = result.scalars().first()
    return user is not None


async def telegram_id_exists(session, telegram_id: int) -> bool:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    return user is not None


async def generate_unique_telegram_id(session, cafe_id: int) -> int:
    telegram_id = TEST_TELEGRAM_ID_BASE + cafe_id

    while await telegram_id_exists(session, telegram_id):
        telegram_id += 1000

    return telegram_id


async def seed_test_managers() -> None:
    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        user_repository = UserRepository(session)

        cafes = await cafe_repository.list_all()
        cafes = [cafe for cafe in cafes if cafe.code != "cafe_center"]

        if not cafes:
            print("Нет кафе для создания тестовых менеджеров.")
            return

        created_count = 0
        skipped_count = 0

        for cafe in cafes:
            exists = await manager_exists_for_cafe(session, cafe.id)
            if exists:
                print(
                    f"[SKIP] У кафе id={cafe.id}, name={cafe.name} менеджер уже существует"
                )
                skipped_count += 1
                continue

            telegram_id = await generate_unique_telegram_id(session, cafe.id)

            user_data = UserCreateSchema(
                telegram_id=telegram_id,
                full_name=f"{TEST_MANAGER_NAME_PREFIX}_{cafe.code}",
                role=ROLE_MANAGER,
                cafe_id=cafe.id,
            )

            user = await user_repository.create(user_data)
            created_count += 1

            print(
                f"[OK] Создан менеджер: "
                f"id={user.id}, telegram_id={user.telegram_id}, "
                f"name={user.full_name}, cafe_id={user.cafe_id}"
            )

        print("\nГотово.")
        print(f"Создано менеджеров: {created_count}")
        print(f"Пропущено кафе: {skipped_count}")


if __name__ == "__main__":
    asyncio.run(seed_test_managers())
