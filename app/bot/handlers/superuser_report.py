from datetime import datetime, time, date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.common import superuser_main_keyboard
from app.bot.keyboards.report import cancel_keyboard
from app.bot.states.superuser_report import SuperuserReportStates
from app.core.constants import ROLE_SUPERUSER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.report_service import ReportService

router = Router()


def parse_date(date_text: str) -> date | None:
    try:
        return datetime.strptime(date_text.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def format_report_text(report) -> str:
    lines = [
        f"Отчёт по кафе ID: {report.cafe_id}",
        f"Период: {report.period.start_date} -> {report.period.end_date}",
        f"Всего анкет: {report.summary.total_surveys}",
        f"Средний балл: {report.summary.average_score:.2f}",
        f"Средний процент: {report.summary.average_percent:.2f}%",
        "",
        "По вопросам:",
        f"Q1: да={report.q1_stats.yes_count}, нет={report.q1_stats.no_count}, "
        f"yes%={report.q1_stats.yes_percent:.2f}",
        f"Q2: да={report.q2_stats.yes_count}, нет={report.q2_stats.no_count}, "
        f"yes%={report.q2_stats.yes_percent:.2f}",
        f"Q3: да={report.q3_stats.yes_count}, нет={report.q3_stats.no_count}, "
        f"yes%={report.q3_stats.yes_percent:.2f}",
        f"Q4: да={report.q4_stats.yes_count}, нет={report.q4_stats.no_count}, "
        f"yes%={report.q4_stats.yes_percent:.2f}",
        "",
        "Распределение оценок:",
        f"100%: {report.score_distribution.percent_100}",
        f"75%: {report.score_distribution.percent_75}",
        f"50%: {report.score_distribution.percent_50}",
        f"25%: {report.score_distribution.percent_25}",
        f"0%: {report.score_distribution.percent_0}",
    ]
    return "\n".join(lines)


@router.message(F.text == "Отчёт по кафе")
async def start_superuser_report(message: Message, state: FSMContext) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        cafe_repository = CafeRepository(session)
        auth_service = AuthService(user_repository)

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)
        if user is None:
            await message.answer("У тебя нет доступа к системе.")
            return

        if user.role != ROLE_SUPERUSER:
            await message.answer("Эта функция доступна только суперюзеру.")
            return

        cafes = await cafe_repository.list_all()
        if not cafes:
            await message.answer("В базе нет кафе.")
            return

        lines = ["Выберите кафе. Введите его ID:\n"]
        for cafe in cafes:
            lines.append(f"{cafe.id} — {cafe.name}")

        await state.clear()
        await message.answer(
            "\n".join(lines),
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(SuperuserReportStates.waiting_for_cafe_id)


@router.message(SuperuserReportStates.waiting_for_cafe_id)
async def process_cafe_id(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("Введите корректный numeric cafe_id.")
        return

    cafe_id = int(text)

    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        cafe = await cafe_repository.get_by_id(cafe_id)

        if cafe is None:
            await message.answer("Кафе с таким ID не найдено.")
            return

    await state.update_data(cafe_id=cafe_id)
    await message.answer(
        "Введите дату начала периода в формате ДД.ММ.ГГГГ",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(SuperuserReportStates.waiting_for_start_date)


@router.message(SuperuserReportStates.waiting_for_start_date)
async def process_start_date(message: Message, state: FSMContext) -> None:
    parsed_date = parse_date(message.text or "")
    if parsed_date is None:
        await message.answer("Неверный формат даты. Используй ДД.ММ.ГГГГ")
        return

    await state.update_data(start_date=parsed_date.isoformat())
    await message.answer(
        "Введите дату конца периода в формате ДД.ММ.ГГГГ",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(SuperuserReportStates.waiting_for_end_date)


@router.message(SuperuserReportStates.waiting_for_end_date)
async def process_end_date(message: Message, state: FSMContext) -> None:
    parsed_end_date = parse_date(message.text or "")
    if parsed_end_date is None:
        await message.answer("Неверный формат даты. Используй ДД.ММ.ГГГГ")
        return

    data = await state.get_data()
    start_date = datetime.fromisoformat(data["start_date"]).date()
    cafe_id = data["cafe_id"]

    if parsed_end_date < start_date:
        await message.answer("Дата конца периода не может быть раньше даты начала.")
        return

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(parsed_end_date, time.max)

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
        if user is None or user.role != ROLE_SUPERUSER:
            await message.answer("Пользователь не найден или не имеет нужных прав.")
            await state.clear()
            return

        report = await report_service.build_cafe_report(
            cafe_id=cafe_id,
            start_date=start_datetime,
            end_date=end_datetime,
        )

    await state.clear()
    await message.answer(
        format_report_text(report),
        reply_markup=superuser_main_keyboard(),
    )


@router.message(F.text == "Отмена")
@router.message(F.text == "/cancel")
async def cancel_superuser_report(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Формирование отчёта отменено.",
        reply_markup=superuser_main_keyboard(),
    )
