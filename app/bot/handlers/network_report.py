from datetime import date, datetime, time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.bot.keyboards.common import superuser_main_keyboard
from app.bot.keyboards.report import cancel_keyboard
from app.bot.states.network_report import NetworkReportStates
from app.core.constants import ROLE_SUPERUSER, SURVEY_QUESTION_LABELS
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.report_service import ReportService
from app.services.excel_report_service import ExcelReportService

router = Router()


def parse_date(date_text: str) -> date | None:
    try:
        return datetime.strptime(date_text.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def format_network_report_text(report) -> str:
    lines = [
        "Общий отчёт по сети",
        f"Период: {report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
        "",
        f"Кафе в отчёте: {report.total_cafes}",
        f"Всего анкет: {report.total_surveys}",
        f"Средний балл: {report.average_score:.2f}",
        f"Средний процент: {report.average_percent:.2f}%",
        "",
        "Распределение оценок:",
        f"100%: {report.distribution.score_100_count}",
        f"75%: {report.distribution.score_75_count}",
        f"50%: {report.distribution.score_50_count}",
        f"25%: {report.distribution.score_25_count}",
        f"0%: {report.distribution.score_0_count}",
        "",
        "По вопросам:",
        f"{SURVEY_QUESTION_LABELS['q1']}: да={report.q1_stats.yes_count}, нет={report.q1_stats.no_count}, да%={report.q1_stats.yes_percent:.2f}",
        f"{SURVEY_QUESTION_LABELS['q2']}: да={report.q2_stats.yes_count}, нет={report.q2_stats.no_count}, да%={report.q2_stats.yes_percent:.2f}",
        f"{SURVEY_QUESTION_LABELS['q3']}: да={report.q3_stats.yes_count}, нет={report.q3_stats.no_count}, да%={report.q3_stats.yes_percent:.2f}",
        f"{SURVEY_QUESTION_LABELS['q4']}: да={report.q4_stats.yes_count}, нет={report.q4_stats.no_count}, да%={report.q4_stats.yes_percent:.2f}",
        "",
        "По кафе:",
    ]

    for cafe in report.cafes:
        lines.append(
            f"{cafe.cafe_id} — {cafe.cafe_name} — {cafe.total_surveys} анкет — {cafe.average_percent:.2f}%"
        )

    return "\n".join(lines)


@router.message(
    NetworkReportStates.waiting_for_start_date,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    NetworkReportStates.waiting_for_end_date,
    F.text.in_({"Отмена", "/cancel"}),
)
async def cancel_network_report(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Формирование отчёта отменено.",
        reply_markup=superuser_main_keyboard(),
    )


@router.message(F.text == "Отчёт по сети")
async def start_network_report(message: Message, state: FSMContext) -> None:
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

    if user.role != ROLE_SUPERUSER:
        await message.answer("Эта функция доступна только суперюзеру.")
        return

    await state.clear()
    await message.answer(
        "Введите дату начала периода в формате ДД.ММ.ГГГГ",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NetworkReportStates.waiting_for_start_date)


@router.message(NetworkReportStates.waiting_for_start_date)
async def process_network_start_date(message: Message, state: FSMContext) -> None:
    parsed_date = parse_date(message.text or "")
    if parsed_date is None:
        await message.answer(
            "Неверный формат даты. Используй ДД.ММ.ГГГГ",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(start_date=parsed_date.isoformat())
    await message.answer(
        "Введите дату конца периода в формате ДД.ММ.ГГГГ",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NetworkReportStates.waiting_for_end_date)


@router.message(NetworkReportStates.waiting_for_end_date)
async def process_network_end_date(message: Message, state: FSMContext) -> None:
    parsed_end_date = parse_date(message.text or "")
    if parsed_end_date is None:
        await message.answer(
            "Неверный формат даты. Используй ДД.ММ.ГГГГ",
            reply_markup=cancel_keyboard(),
        )
        return

    data = await state.get_data()
    start_date = datetime.fromisoformat(data["start_date"]).date()

    if parsed_end_date < start_date:
        await message.answer(
            "Дата конца периода не может быть раньше даты начала.",
            reply_markup=cancel_keyboard(),
        )
        return

    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        await state.clear()
        return

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(parsed_end_date, time.max)

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        survey_repository = SurveyRepository(session)
        cafe_repository = CafeRepository(session)

        auth_service = AuthService(user_repository)
        report_service = ReportService(
            survey_repository=survey_repository,
            cafe_repository=cafe_repository,
        )
        excel_report_service = ExcelReportService()

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)
        if user is None or user.role != ROLE_SUPERUSER:
            await message.answer("Пользователь не найден или не имеет нужных прав.")
            await state.clear()
            return

        report = await report_service.build_network_report(
            start_date=start_datetime,
            end_date=end_datetime,
        )
        excel_file_path = excel_report_service.build_network_report_file(report)

    await state.clear()
    await message.answer(
        format_network_report_text(report),
        reply_markup=superuser_main_keyboard(),
    )
    await message.answer_document(
        FSInputFile(excel_file_path),
        caption="Excel-отчёт по сети готов.",
    )
