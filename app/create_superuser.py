import asyncio

from app.core.constants import ROLE_SUPERUSER
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateSchema


async def create_superuser() -> None:
    telegram_id = int(input("Введите ваш Telegram ID: "))
    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)

        existing_user = await user_repository.get_by_telegram_id(telegram_id)
        if existing_user is not None:
            print(
                f"Пользователь уже существует: "
                f"id={existing_user.id}, role={existing_user.role}"
            )
            return

        user = await user_repository.create(
            UserCreateSchema(
                telegram_id=telegram_id,
                full_name="megasuper_user",
                role=ROLE_SUPERUSER,
                cafe_id=None,
            )
        )
        print(f"Создан суперюзер: id={user.id}, telegram_id={user.telegram_id}")


if __name__ == "__main__":
    asyncio.run(create_superuser())
