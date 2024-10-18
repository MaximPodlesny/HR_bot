from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    behavior = State()
    reason = State()
    frequency = State()
    reaction = State()
    measures = State()
    goal = State()
    commitment = State()
