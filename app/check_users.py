import asyncio

from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal


async def check_users() -> None:
    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        users = await user_repository.list_all()

        if not users:
            print("Пользователи не найдены.")
            return

        for user in users:
            print(
                f"id={user.id}, "
                f"telegram_id={user.telegram_id}, "
                f"full_name={user.full_name}, "
                f"role={user.role}, "
                f"cafe_id={user.cafe_id}, "
                f"is_active={user.is_active}"
            )


if __name__ == "__main__":
    asyncio.run(check_users())
