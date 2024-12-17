from handlers.utils.get_admin_ids import get_admins
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup

class UserchatInfoStates(StatesGroup):
       admin_ids = State()
def g_a():
    global ADMINS
    ADMINS = get_admins()
    print(ADMINS)
    # data = await state.get_data()
    # data['admin_ids'] = get_admins()
    # ids = data.get('admin_ids')

g_a()