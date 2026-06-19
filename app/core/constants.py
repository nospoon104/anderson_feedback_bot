ROLE_MANAGER = "manager"
ROLE_SUPERUSER = "superuser"

ROLES = {ROLE_MANAGER, ROLE_SUPERUSER}

MAX_COMMENT_LENGTH = 1000

UNKNOWN_TABLE_NUMBER = 0
MIN_TABLE_NUMBER = 1
MAX_TABLE_NUMBER = 1000

GUEST_TABLE_NUMBER = 0

SURVEY_QUESTIONS = {
    "q1": "Меня встретили радушно, проявили заботу и проводили до стола.",
    "q2": "Официант хорошо ориентировался в меню: подробно проконсультировал и помог с выбором блюд и напитков.",
    "q3": "Мне понравился вкус блюд и напитков.",
    "q4": "Скорость обслуживания полностью соответствовала моим ожиданиям.",
}

SURVEY_QUESTION_LABELS = {
    "q1": "Встреча и сопровождение до стола",
    "q2": "Консультация по меню",
    "q3": "Вкус блюд и напитков",
    "q4": "Скорость обслуживания",
}

ROLE_GUEST = "guest"

ROLES = {ROLE_MANAGER, ROLE_SUPERUSER, ROLE_GUEST}

GUEST_SURVEY_START_PREFIX = "guest_"
GUEST_TABLE_NUMBER = 0

GUEST_SURVEY_WELCOME_TEXT = (
    "Здравствуйте!\n\n"
    "Спасибо, что посетили наше кафе.\n"
    "Пожалуйста, ответьте на 4 коротких вопроса о вашем визите.\n"
    "Это займёт меньше минуты."
)

GUEST_SURVEY_THANK_YOU_TEXT = (
    "Спасибо за ваш отзыв! 💛\n\n" "Ваш ответ сохранён и поможет нам улучшать сервис."
)
