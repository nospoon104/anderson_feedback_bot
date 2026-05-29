from aiogram import Bot, Dispatcher


from app.bot.handlers.report import router as report_router
from app.bot.handlers.start import router as start_router
from app.bot.handlers.survey import router as survey_router
from app.core.config import settings


def create_bot() -> Bot:
    return Bot(token=settings.bot_token)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(survey_router)
    dp.include_router(report_router)
    return dp
