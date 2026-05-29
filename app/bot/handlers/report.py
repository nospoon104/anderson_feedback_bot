from datetime import datetime, time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.common import manager_main_keyboard
from app.bot.keyboards.report import report_cancel_keyboard
from app.bot.states.report import ReportStates
from app.core.constants import ROLE_MANAGER
from app.db.repositories.survey_repository import SurveyRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.report_service import ReportService

router = Router()


def parse_date(text: str) -> datetime | None:
    text = text.strip()
    try:
        return datetime.strptime(text, "%d.%m.%Y")
    except ValueError:
        return None


def format_report_text(report) -> str:
    return (
        f"Отчёт по кафе #{report.cafe_id}\n"
        f"Период: {report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}\n\n"
        f"Всего анкет: {report.summary.total_surveys}\n"
        f"Средний балл: {report.summary.average_score}\n"
        f"Общий процент: {report.summary.average_percent}%\n\n"
        f"Распределение анкет:\n"
        f"100%: {report.summary.distribution.score_100_count}\n"
        f"75%: {report.summary.distribution.score_75_count}\n"
        f"50%: {report.summary.distribution.score_50_count}\n"
        f"25%: {report.summary.distribution.score_25_count}\n"
        f"0%: {report.summary.distribution.score_0_count}\n\n"
        f"По вопросам:\n"
        f"Q1: Да={report.q1_stats.yes_count}, Нет={report.q1_stats.no_count}, "
        f"Да%={report.q1_stats.yes_percent}\n"
        f"Q2: Да={report.q2_stats.yes_count}, Нет={report.q2_stats.no_count}, "
        f"Да%={report.q2_stats.yes_percent}\n"
        f"Q3: Да={report.q3_stats.yes_count}, Нет={report.q3_stats.no_count}, "
        f"Да%={report.q3_stats.yes_percent}\n"
        f"Q4: Да={report.q4_stats.yes_count}, Нет={report.q4_stats.no_count}, "
        f"Да%={report.q4_stats.yes_percent}\n\n"
        f"Сравнение с предыдущим периодом:\n"
        f"Текущий период: {report.comparison.current_average_percent}%\n"
        f"Предыдущий период: {report.comparison.previous_average_percent}%\n"
        f"Разница: {report.comparison.delta_percent_points} п.п."
    )


@router.message(F.text == "Отчёт за период")
async def start_report(message: Message, state: FSMContext) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        auth_service = AuthService(user_repository)
        user = await auth_service.get_user_by_telegram_id(telegram_user.id)

    if user is None:
        await message.answer("У тебя нет доступа к системе.")
        return

    if user.role != ROLE_MANAGER:
        await message.answer("Этот отчёт доступен только менеджерам.")
        return

    await state.clear()
    await message.answer(
        "Введите дату начала периода в формате ДД.ММ.ГГГГ",
        reply_markup=report_cancel_keyboard(),
    )
    await state.set_state(ReportStates.waiting_for_start_date)


@router.message(ReportStates.waiting_for_start_date)
async def process_report_start_date(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().lower() == "отмена":
        await state.clear()
        await message.answer(
            "Формирование отчёта отменено.",
            reply_markup=manager_main_keyboard(),
        )
        return

    start_date = parse_date(message.text or "")
    if start_date is None:
        await message.answer("Неверный формат даты. Введите ДД.ММ.ГГГГ")
        return

    await state.update_data(start_date=start_date.isoformat())
    await message.answer(
        "Введите дату конца периода в формате ДД.ММ.ГГГГ",
        reply_markup=report_cancel_keyboard(),
    )
    await state.set_state(ReportStates.waiting_for_end_date)


@router.message(ReportStates.waiting_for_end_date)
async def process_report_end_date(message: Message, state: FSMContext) -> None:
    if (message.text or "").strip().lower() == "отмена":
        await state.clear()
        await message.answer(
            "Формирование отчёта отменено.",
            reply_markup=manager_main_keyboard(),
        )
        return

    end_date_raw = parse_date(message.text or "")
    if end_date_raw is None:
        await message.answer("Неверный формат даты. Введите ДД.ММ.ГГГГ")
        return

    data = await state.get_data()
    start_date = datetime.fromisoformat(data["start_date"])

    start_datetime = datetime.combine(start_date.date(), time.min)
    end_datetime = datetime.combine(end_date_raw.date(), time.max)

    if end_datetime < start_datetime:
        await message.answer("Дата конца периода не может быть раньше даты начала.")
        return

    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        survey_repository = SurveyRepository(session)

        auth_service = AuthService(user_repository)
        report_service = ReportService(survey_repository)

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)
        if user is None or user.cafe_id is None:
            await message.answer("Пользователь не найден или не привязан к кафе.")
            await state.clear()
            return

        report = await report_service.build_cafe_report(
            cafe_id=user.cafe_id,
            start_date=start_datetime,
            end_date=end_datetime,
        )

    await state.clear()
    await message.answer(
        format_report_text(report),
        reply_markup=manager_main_keyboard(),
    )
