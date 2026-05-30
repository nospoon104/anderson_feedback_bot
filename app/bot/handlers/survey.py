from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.common import manager_main_keyboard
from app.bot.keyboards.survey import (
    cancel_keyboard,
    skip_comment_keyboard,
    yes_no_keyboard,
)
from app.bot.states.survey import SurveyStates
from app.core.constants import ROLE_MANAGER, SURVEY_QUESTIONS
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


@router.message(
    SurveyStates.waiting_for_visit_datetime,
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
        "Введите дату и время визита в формате ДД.ММ.ГГГГ ЧЧ:ММ\n"
        "Например: 28.05.2026 19:30",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(SurveyStates.waiting_for_visit_datetime)


@router.message(SurveyStates.waiting_for_visit_datetime)
async def process_visit_datetime(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    try:
        visit_datetime = datetime.strptime(text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            "Неверный формат даты.\n" "Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(visit_datetime=visit_datetime.isoformat())
    await message.answer("Введите номер стола:", reply_markup=cancel_keyboard())
    await state.set_state(SurveyStates.waiting_for_table_number)


@router.message(SurveyStates.waiting_for_table_number)
async def process_table_number(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if not text.isdigit():
        await message.answer(
            "Номер стола должен быть целым положительным числом.",
            reply_markup=cancel_keyboard(),
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
            "Пожалуйста, используй кнопки Да / Нет.", reply_markup=yes_no_keyboard()
        )
        return

    await state.update_data(q1=answer)
    await message.answer(SURVEY_QUESTIONS["q2"], reply_markup=yes_no_keyboard())
    await state.set_state(SurveyStates.waiting_for_q2)


@router.message(SurveyStates.waiting_for_q2)
async def process_q2(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.", reply_markup=yes_no_keyboard()
        )
        return

    await state.update_data(q2=answer)
    await message.answer(SURVEY_QUESTIONS["q3"], reply_markup=yes_no_keyboard())
    await state.set_state(SurveyStates.waiting_for_q3)


@router.message(SurveyStates.waiting_for_q3)
async def process_q3(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.", reply_markup=yes_no_keyboard()
        )
        return

    await state.update_data(q3=answer)
    await message.answer(SURVEY_QUESTIONS["q4"], reply_markup=yes_no_keyboard())
    await state.set_state(SurveyStates.waiting_for_q4)


@router.message(SurveyStates.waiting_for_q4)
async def process_q4(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используй кнопки Да / Нет.", reply_markup=yes_no_keyboard()
        )
        return

    await state.update_data(q4=answer)
    await message.answer(
        "Введите комментарий к анкете или нажми 'Пропустить'.",
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
