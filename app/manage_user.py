import asyncio

from app.core.constants import ROLE_MANAGER, ROLE_SUPERUSER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreateSchema


def print_role_choices() -> None:
    print("Выберите роль:")
    print("1 - superuser")
    print("2 - manager")


def get_role_from_input(role_choice: str) -> str | None:
    role_map = {
        "1": ROLE_SUPERUSER,
        "2": ROLE_MANAGER,
    }
    return role_map.get(role_choice)


def print_cafes(cafes) -> None:
    print("\nДоступные кафе:")
    for cafe in cafes:
        print(f"  id={cafe.id} | {cafe.name} | code={cafe.code}")
    print()


async def create_or_update_user() -> None:
    telegram_id_raw = input("Введите Telegram ID пользователя: ").strip()
    if not telegram_id_raw.isdigit():
        print("Telegram ID должен быть числом.")
        return

    telegram_id = int(telegram_id_raw)
    full_name = input("Введите имя пользователя: ").strip()

    if not full_name:
        print("Имя не может быть пустым.")
        return

    print_role_choices()
    role_choice = input("Введите номер роли: ").strip()

    role = get_role_from_input(role_choice)
    if role is None:
        print("Некорректный выбор роли.")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        cafe_repository = CafeRepository(session)

        cafe_id = None

        if role == ROLE_MANAGER:
            cafes = await cafe_repository.list_all()

            if not cafes:
                print("В базе нет кафе. Сначала заполни cafes через seed_cafes.py")
                return

            print_cafes(cafes)

            cafe_id_raw = input("Введите cafe_id для менеджера: ").strip()
            if not cafe_id_raw.isdigit():
                print("cafe_id должен быть числом.")
                return

            cafe_id = int(cafe_id_raw)

            cafe = await cafe_repository.get_by_id(cafe_id)
            if cafe is None:
                print(f"Кафе с id={cafe_id} не найдено.")
                return

        existing_user = await user_repository.get_by_telegram_id(telegram_id)

        if existing_user is not None:
            existing_user.full_name = full_name
            existing_user.role = role
            existing_user.cafe_id = cafe_id

            await session.commit()
            await session.refresh(existing_user)

            print(
                "Пользователь обновлён:\n"
                f"  id={existing_user.id}\n"
                f"  telegram_id={existing_user.telegram_id}\n"
                f"  full_name={existing_user.full_name}\n"
                f"  role={existing_user.role}\n"
                f"  cafe_id={existing_user.cafe_id}"
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
            "Пользователь создан:\n"
            f"  id={user.id}\n"
            f"  telegram_id={user.telegram_id}\n"
            f"  full_name={user.full_name}\n"
            f"  role={user.role}\n"
            f"  cafe_id={user.cafe_id}"
        )


if __name__ == "__main__":
    asyncio.run(create_or_update_user())
