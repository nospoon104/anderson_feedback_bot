from aiogram import Bot, Dispatcher

from app.bot.handlers.network_report import router as network_report_router
from app.bot.handlers.report import router as report_router
from app.bot.handlers.start import router as start_router
from app.bot.handlers.superuser_report import router as superuser_report_router
from app.bot.handlers.survey import router as survey_router
from app.bot.handlers.guest_qr import router as guest_qr_router
from app.bot.handlers.guest_survey import router as guest_survey_router
from app.core.config import settings


def create_bot() -> Bot:
    return Bot(token=settings.bot_token)


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(survey_router)
    dispatcher.include_router(guest_survey_router)
    dispatcher.include_router(guest_qr_router)
    dispatcher.include_router(report_router)
    dispatcher.include_router(superuser_report_router)
    dispatcher.include_router(network_report_router)
    return dispatcher
