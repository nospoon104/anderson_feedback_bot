import asyncio

from app.core.constants import ROLE_MANAGER, ROLE_SUPERUSER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateSchema


async def create_or_update_user() -> None:
    telegram_id = int(input("Введите ваш Telegram ID: "))
    full_name = input("Введите имя [megasuper_user]: ").strip() or "megasuper_user"

    print("Выберите роль:")
    print("1 - superuser")
    print("2 - manager")
    role_choice = input("Введите номер роли: ").strip()

    role_map = {
        "1": ROLE_SUPERUSER,
        "2": ROLE_MANAGER,
    }

    role = role_map.get(role_choice)
    if role is None:
        print("Некорректный выбор роли")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        cafe_repository = CafeRepository(session)

        cafe_id = None

        if role == ROLE_MANAGER:
            cafe_id_input = input("Введите cafe_id для менеджера: ").strip()

            if not cafe_id_input.isdigit():
                print("cafe_id должен быть числом")
                return

            cafe_id = int(cafe_id_input)

            cafe = await cafe_repository.get_by_id(cafe_id)
            if cafe is None:
                print(f"Кафе с id={cafe_id} не найдено")
                return

        existing_user = await user_repository.get_by_telegram_id(telegram_id)
        if existing_user is not None:
            existing_user.full_name = full_name
            existing_user.role = role
            existing_user.cafe_id = cafe_id

            await session.commit()
            await session.refresh(existing_user)

            print(
                f"Пользователь обновлен: "
                f"id={existing_user.id}, "
                f"telegram_id={existing_user.telegram_id}, "
                f"role={existing_user.role}, "
                f"cafe_id={existing_user.cafe_id}"
            )
            return

        user = await user_repository.create(
            UserCreateSchema(
                telegram_id=telegram_id,
                full_name=full_name,
                role=role,
                cafe_id=cafe_id,
            )
        )

        print(
            f"Пользователь создан: "
            f"id={user.id}, "
            f"telegram_id={user.telegram_id}, "
            f"role={user.role}, "
            f"cafe_id={user.cafe_id}"
        )


if __name__ == "__main__":
    asyncio.run(create_or_update_user())
