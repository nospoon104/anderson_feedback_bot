from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def skip_comment_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
