from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def manager_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить анкету")],
            [KeyboardButton(text="Отчёт за период")],
        ],
        resize_keyboard=True,
    )


def superuser_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отчёт по кафе")],
            [KeyboardButton(text="Отчёт по сети")],
            [KeyboardButton(text="Управление пользователями")],
        ],
        resize_keyboard=True,
    )
