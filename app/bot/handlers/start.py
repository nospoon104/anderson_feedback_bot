from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.handlers.guest_survey import start_guest_survey
from app.bot.keyboards.common import (
    manager_main_keyboard,
    superuser_main_keyboard,
)
from app.core.constants import GUEST_SURVEY_START_PREFIX, ROLE_MANAGER, ROLE_SUPERUSER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    start_arg = parts[1] if len(parts) > 1 else None

    async with AsyncSessionLocal() as session:
        if start_arg and start_arg.startswith(GUEST_SURVEY_START_PREFIX):
            guest_token = start_arg.removeprefix(GUEST_SURVEY_START_PREFIX)
            cafe_repository = CafeRepository(session)
            cafe = await cafe_repository.get_by_guest_token(guest_token)

            if cafe is None or not cafe.is_active:
                await message.answer(
                    "Ссылка для анкеты недействительна или кафе недоступно."
                )
                return

            await start_guest_survey(
                message=message,
                state=state,
                cafe_id=cafe.id,
                cafe_name=cafe.name,
            )
            return

        user_repository = UserRepository(session)
        auth_service = AuthService(user_repository)
        user = await auth_service.get_user_by_telegram_id(telegram_user.id)

    if user is None:
        await message.answer(
            "Привет!\n\n"
            "Если вы хотели оставить отзыв по QR-коду, откройте ссылку из QR ещё раз.\n"
            "Если вы сотрудник, обратитесь к администратору для доступа."
        )
        return

    await state.clear()

    if user.role == ROLE_MANAGER:
        await message.answer(
            f"Привет, {user.full_name}.\nТы авторизован как менеджер.",
            reply_markup=manager_main_keyboard(),
        )
        return

    if user.role == ROLE_SUPERUSER:
        await message.answer(
            f"Привет, {user.full_name}.\nТы авторизован как суперюзер.",
            reply_markup=superuser_main_keyboard(),
        )
        return

    await message.answer("Роль пользователя не распознана.")
