from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message

from app.core.constants import ROLE_MANAGER, ROLE_SUPERUSER, GUEST_SURVEY_START_PREFIX
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.qr_service import QRService

router = Router()


@router.message(F.text == "QR-код для гостей")
async def send_guest_qr(message: Message) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    if not bot_username:
        await message.answer("Не удалось определить username бота.")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        cafe_repository = CafeRepository(session)
        auth_service = AuthService(user_repository)

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)

        if user is None:
            await message.answer("У тебя нет доступа к системе.")
            return

        if user.role != ROLE_MANAGER:
            await message.answer("QR-код доступен только менеджеру привязанного кафе.")
            return

        if user.cafe_id is None:
            await message.answer("Менеджер не привязан к кафе.")
            return

        cafe = await cafe_repository.get_by_id(user.cafe_id)
        if cafe is None:
            await message.answer("Кафе не найдено.")
            return

        link = (
            f"https://t.me/{bot_username}"
            f"?start={GUEST_SURVEY_START_PREFIX}{cafe.guest_token}"
        )

        qr_bytes = QRService.build_qr_image_bytes(link)
        qr_file = BufferedInputFile(
            qr_bytes.getvalue(),
            filename=f"guest_qr_cafe_{cafe.id}.png",
        )

        await message.answer_document(
            qr_file,
            caption=(
                f"QR-код для гостей кафе «{cafe.name}».\n\n"
                f"Гость может отсканировать код и сразу заполнить анкету в Telegram.\n"
                f"Файл можно распечатать и разместить в кафе."
            ),
        )
