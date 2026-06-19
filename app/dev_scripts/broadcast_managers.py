import asyncio

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.bot.bot import create_bot
from app.core.constants import ROLE_MANAGER
from app.db.models import User
from app.db.session import AsyncSessionLocal
from sqlalchemy import select


def read_multiline_message() -> str:
    print("Введите текст сообщения.")
    print("Когда закончите ввод, напишите в новой строке: END")
    print()

    lines: list[str] = []

    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines).strip()


async def get_manager_users() -> list[User]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .where(User.role == ROLE_MANAGER, User.is_active.is_(True))
            .order_by(User.id)
        )
        return list(result.scalars().all())


async def broadcast_to_managers() -> None:
    users = await get_manager_users()

    if not users:
        print("Активные менеджеры не найдены.")
        return

    print(f"Найдено менеджеров: {len(users)}")
    print()

    message_text = read_multiline_message()
    if not message_text:
        print("Пустое сообщение. Рассылка отменена.")
        return

    print()
    print("Предпросмотр сообщения:")
    print("-" * 40)
    print(message_text)
    print("-" * 40)
    print()

    confirm = (
        input("Отправить это сообщение всем менеджерам? (yes/no): ").strip().lower()
    )
    if confirm not in {"yes", "y"}:
        print("Рассылка отменена.")
        return

    bot = create_bot()

    sent_count = 0
    failed_count = 0

    try:
        for user in users:
            try:
                await bot.send_message(chat_id=user.telegram_id, text=message_text)
                print(
                    f"[OK] id={user.id} telegram_id={user.telegram_id} name={user.full_name}"
                )
                sent_count += 1

            except TelegramForbiddenError:
                print(
                    f"[FORBIDDEN] id={user.id} telegram_id={user.telegram_id} "
                    f"name={user.full_name} | пользователь заблокировал бота "
                    f"или не запускал его"
                )
                failed_count += 1

            except TelegramBadRequest as exc:
                print(
                    f"[BAD_REQUEST] id={user.id} telegram_id={user.telegram_id} "
                    f"name={user.full_name} | {exc}"
                )
                failed_count += 1

            except Exception as exc:
                print(
                    f"[ERROR] id={user.id} telegram_id={user.telegram_id} "
                    f"name={user.full_name} | {type(exc).__name__}: {exc}"
                )
                failed_count += 1

            await asyncio.sleep(0.05)

    finally:
        await bot.session.close()

    print()
    print("Рассылка завершена.")
    print(f"Успешно отправлено: {sent_count}")
    print(f"Ошибок: {failed_count}")


if __name__ == "__main__":
    asyncio.run(broadcast_to_managers())
