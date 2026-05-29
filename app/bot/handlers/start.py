from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.constants import ROLE_MANAGER, ROLE_SUPERUSER
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.bot.keyboards.common import (
    manager_main_keyboard,
    superuser_main_keyboard,
)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    telegram_user = message.from_user

    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        auth_service = AuthService(user_repository)

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)

    if user is None:
        await message.answer(
            "Привет. У тебя пока нет доступа к системе.\n"
            "Обратись к администратору, чтобы тебя добавили."
        )
        return

    if user.role == ROLE_MANAGER:
        await message.answer(
            f"Привет, {user.full_name}.\n" "Ты авторизован как менеджер.",
            reply_markup=manager_main_keyboard(),
        )
        return

    if user.role == ROLE_SUPERUSER:
        await message.answer(
            f"Привет, {user.full_name}.\n" "Ты авторизован как суперюзер.",
            reply_markup=superuser_main_keyboard(),
        )
        return

    await message.answer("Роль пользователя не распознана.")
