from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.common import manager_main_keyboard
from app.bot.keyboards.survey import (
    skip_comment_keyboard,
    survey_date_keyboard,
    table_keyboard,
    time_keyboard,
    yes_no_keyboard,
)
from app.bot.states.survey import SurveyStates
from app.core.constants import ROLE_MANAGER, SURVEY_QUESTIONS, UNKNOWN_TABLE_NUMBER
from app.db.repositories.survey_repository import SurveyRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.services.survey_service import SurveyService

router = Router()


def parse_yes_no(text: str) -> bool | None:
    normalized = text.strip().lower()
    if normalized == "да":
        return True
    if normalized == "нет":
        return False
    return None


def parse_manual_date(text: str) -> datetime | None:
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y")
    except ValueError:
        return None


def parse_time_text(text: str) -> tuple[int, int] | None:
    try:
        parsed = datetime.strptime(text.strip(), "%H:%M")
        return parsed.hour, parsed.minute
    except ValueError:
        return None


def resolve_quick_date(text: str) -> datetime | None:
    normalized = text.strip().lower()
    today = datetime.now()

    if normalized == "сегодня":
        return today
    if normalized == "вчера":
        return today - timedelta(days=1)
    if normalized == "позавчера":
        return today - timedelta(days=2)

    return None


@router.message(F.text == "Главное меню")
async def go_to_main_menu(message: Message, state: FSMContext) -> None:
    telegram_user = message.from_user
    await state.clear()

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

    if user.role == ROLE_MANAGER:
        await message.answer(
            "Возвращаю в главное меню.",
            reply_markup=manager_main_keyboard(),
        )
        return

    await message.answer("Главное меню недоступно для этой роли.")


@router.message(
    SurveyStates.waiting_for_visit_date_choice,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_visit_date_manual,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_visit_time,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_table_number,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_q1,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_q2,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_q3,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_q4,
    F.text.in_({"Отмена", "/cancel"}),
)
@router.message(
    SurveyStates.waiting_for_comment,
    F.text.in_({"Отмена", "/cancel"}),
)
async def cancel_survey(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Ввод анкеты отменён.",
        reply_markup=manager_main_keyboard(),
    )


@router.message(F.text == "Добавить анкету")
async def start_survey(message: Message, state: FSMContext) -> None:
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
        await message.answer("Добавление анкет доступно только менеджерам.")
        return

    await state.clear()
    await message.answer(
        "Выберите дату визита:",
        reply_markup=survey_date_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_visit_date_choice)


@router.message(SurveyStates.waiting_for_visit_date_choice)
async def process_visit_date_choice(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    quick_date = resolve_quick_date(text)
    if quick_date is not None:
        await state.update_data(visit_date=quick_date.date().isoformat())
        await message.answer(
            "Введите время визита в формате ЧЧ:ММ\nНапример: 19:30",
            reply_markup=time_keyboard(),
        )
        await state.set_state(SurveyStates.waiting_for_visit_time)
        return

    if text == "Ввести вручную":
        await message.answer(
            "Введите дату визита в формате ДД.ММ.ГГГГ\nНапример: 28.05.2026",
            reply_markup=time_keyboard(),
        )
        await state.set_state(SurveyStates.waiting_for_visit_date_manual)
        return

    await message.answer(
        "Выберите дату кнопкой: Сегодня, Вчера, Позавчера или Ввести вручную.",
        reply_markup=survey_date_keyboard(),
    )


@router.message(SurveyStates.waiting_for_visit_date_manual)
async def process_visit_date_manual(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    quick_date = resolve_quick_date(text)
    if quick_date is not None:
        await state.update_data(visit_date=quick_date.date().isoformat())
        await message.answer(
            "Введите время визита в формате ЧЧ:ММ\nНапример: 19:30",
            reply_markup=time_keyboard(),
        )
        await state.set_state(SurveyStates.waiting_for_visit_time)
        return

    visit_date = parse_manual_date(text)
    if visit_date is None:
        await message.answer(
            "Неверный формат даты. Введите ДД.ММ.ГГГГ",
            reply_markup=time_keyboard(),
        )
        return

    await state.update_data(visit_date=visit_date.date().isoformat())
    await message.answer(
        "Введите время визита в формате ЧЧ:ММ\nНапример: 19:30",
        reply_markup=time_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_visit_time)


@router.message(SurveyStates.waiting_for_visit_time)
async def process_visit_time(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    parsed_time = parse_time_text(text)
    if parsed_time is None:
        await message.answer(
            "Неверный формат времени. Введите ЧЧ:ММ\nНапример: 19:30",
            reply_markup=time_keyboard(),
        )
        return

    hour, minute = parsed_time
    data = await state.get_data()
    visit_date = datetime.fromisoformat(data["visit_date"]).date()
    visit_datetime = datetime.combine(visit_date, datetime.min.time()).replace(
        hour=hour,
        minute=minute,
    )

    await state.update_data(visit_datetime=visit_datetime.isoformat())
    await message.answer(
        "Введите номер стола или нажмите «Без номера стола».",
        reply_markup=table_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_table_number)


@router.message(SurveyStates.waiting_for_table_number)
async def process_table_number(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if text == "Без номера стола":
        table_number = UNKNOWN_TABLE_NUMBER
    else:
        if not text.isdigit():
            await message.answer(
                "Введите номер стола числом или нажмите «Без номера стола».",
                reply_markup=table_keyboard(),
            )
            return
        table_number = int(text)

    await state.update_data(table_number=table_number)

    await message.answer(
        SURVEY_QUESTIONS["q1"],
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_q1)


@router.message(SurveyStates.waiting_for_q1)
async def process_q1(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q1=answer)
    await message.answer(
        SURVEY_QUESTIONS["q2"],
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_q2)


@router.message(SurveyStates.waiting_for_q2)
async def process_q2(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q2=answer)
    await message.answer(
        SURVEY_QUESTIONS["q3"],
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_q3)


@router.message(SurveyStates.waiting_for_q3)
async def process_q3(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q3=answer)
    await message.answer(
        SURVEY_QUESTIONS["q4"],
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_q4)


@router.message(SurveyStates.waiting_for_q4)
async def process_q4(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q4=answer)
    await message.answer(
        "Введите комментарий к анкете или нажмите «Пропустить».",
        reply_markup=skip_comment_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_comment)


@router.message(SurveyStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        await state.clear()
        return

    comment_text = (message.text or "").strip()
    if comment_text.lower() == "пропустить":
        comment_text = None

    data = await state.get_data()

    visit_datetime = datetime.fromisoformat(data["visit_datetime"])
    table_number = data["table_number"]
    q1 = data["q1"]
    q2 = data["q2"]
    q3 = data["q3"]
    q4 = data["q4"]

    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        survey_repository = SurveyRepository(session)

        auth_service = AuthService(user_repository)
        survey_service = SurveyService(survey_repository)

        user = await auth_service.get_user_by_telegram_id(telegram_user.id)
        if user is None:
            await message.answer("Пользователь не найден в системе.")
            await state.clear()
            return

        try:
            survey = await survey_service.create_survey(
                manager=user,
                visit_datetime=visit_datetime,
                table_number=table_number,
                q1=q1,
                q2=q2,
                q3=q3,
                q4=q4,
                comment_text=comment_text,
            )
        except ValueError as exc:
            await message.answer(
                f"Не удалось сохранить анкету: {exc}",
                reply_markup=manager_main_keyboard(),
            )
            await state.clear()
            return

    await state.clear()
    await message.answer(
        f"Анкета сохранена. ID анкеты: {survey.id}",
        reply_markup=manager_main_keyboard(),
    )
