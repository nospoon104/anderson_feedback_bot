from aiogram.fsm.state import State, StatesGroup


class ReportStates(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()
