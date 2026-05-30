from aiogram.fsm.state import State, StatesGroup


class SuperuserReportStates(StatesGroup):
    waiting_for_cafe_id = State()
    waiting_for_start_date = State()
    waiting_for_end_date = State()
