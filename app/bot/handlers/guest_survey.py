from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.survey import skip_comment_keyboard, yes_no_keyboard
from app.bot.states.guest_survey import GuestSurveyStates
from app.core.constants import SURVEY_QUESTIONS
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.session import AsyncSessionLocal
from app.services.survey_service import SurveyService

router = Router()


def parse_yes_no(text: str) -> bool | None:
    normalized = text.strip().lower()
    if normalized == "да":
        return True
    if normalized == "нет":
        return False
    return None


async def start_guest_survey(
    message: Message,
    state: FSMContext,
    cafe_id: int,
    cafe_name: str,
) -> None:
    await state.clear()
    await state.update_data(cafe_id=cafe_id)

    await message.answer(
        f"Спасибо, что посетили кафе «{cafe_name}».\n\n"
        f"Пожалуйста, ответьте на 4 коротких вопроса.\n\n"
        f"Вопрос 1 из 4:\n{SURVEY_QUESTIONS['q1']}",
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(GuestSurveyStates.waiting_for_q1)


@router.message(GuestSurveyStates.waiting_for_q1)
async def process_guest_q1(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используйте кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q1=answer)
    await message.answer(
        f"Вопрос 2 из 4:\n{SURVEY_QUESTIONS['q2']}",
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(GuestSurveyStates.waiting_for_q2)


@router.message(GuestSurveyStates.waiting_for_q2)
async def process_guest_q2(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используйте кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q2=answer)
    await message.answer(
        f"Вопрос 3 из 4:\n{SURVEY_QUESTIONS['q3']}",
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(GuestSurveyStates.waiting_for_q3)


@router.message(GuestSurveyStates.waiting_for_q3)
async def process_guest_q3(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используйте кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q3=answer)
    await message.answer(
        f"Вопрос 4 из 4:\n{SURVEY_QUESTIONS['q4']}",
        reply_markup=yes_no_keyboard(),
    )
    await state.set_state(GuestSurveyStates.waiting_for_q4)


@router.message(GuestSurveyStates.waiting_for_q4)
async def process_guest_q4(message: Message, state: FSMContext) -> None:
    answer = parse_yes_no(message.text or "")
    if answer is None:
        await message.answer(
            "Пожалуйста, используйте кнопки Да / Нет.",
            reply_markup=yes_no_keyboard(),
        )
        return

    await state.update_data(q4=answer)
    await message.answer(
        "Если хотите, оставьте комментарий одним сообщением.\n"
        "Если комментария нет — нажмите «Пропустить».",
        reply_markup=skip_comment_keyboard(),
    )
    await state.set_state(GuestSurveyStates.waiting_for_comment)


@router.message(GuestSurveyStates.waiting_for_comment)
async def process_guest_comment(message: Message, state: FSMContext) -> None:
    comment_text = (message.text or "").strip()
    if comment_text.lower() == "пропустить":
        comment_text = None

    data = await state.get_data()
    cafe_id = data["cafe_id"]

    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        survey_repository = SurveyRepository(session)
        survey_service = SurveyService(survey_repository)

        cafe = await cafe_repository.get_by_id(cafe_id)
        if cafe is None:
            await message.answer("Не удалось определить кафе для анкеты.")
            await state.clear()
            return

        try:
            await survey_service.create_guest_survey(
                cafe=cafe,
                q1=data["q1"],
                q2=data["q2"],
                q3=data["q3"],
                q4=data["q4"],
                comment_text=comment_text,
            )
        except ValueError:
            await message.answer(
                "Не удалось сохранить отзыв. Пожалуйста, попробуйте ещё раз позже."
            )
            await state.clear()
            return

    await state.clear()
    await message.answer("Спасибо! Ваш отзыв сохранён 💛")
