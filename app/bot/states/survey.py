from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    waiting_for_visit_datetime = State()
    waiting_for_table_number = State()
    waiting_for_q1 = State()
    waiting_for_q2 = State()
    waiting_for_q3 = State()
    waiting_for_q4 = State()
    waiting_for_comment = State()
