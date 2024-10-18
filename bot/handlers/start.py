from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .vacancy import VacancyStates

from bot.utils import message_utils

class StartStates(StatesGroup):
    choose_action = State()

async def process_start_command(message: types.Message, state: FSMContext):
    """Handles the `/start` command."""
    await message.reply(message_utils.format_start_message())
    await state.set_state(StartStates.choose_action.state)

async def process_choose_action(message: types.Message, state: FSMContext):
    """Handles user choice after `/start`."""
    if message.text == "Создать вакансию":
        await message.reply(message_utils.format_create_vacancy_message())
        await state.set_state(VacancyStates.collecting_info.state)
    elif message.text == "Добавить кандидата":
        await message.reply(message_utils.format_add_candidate_message())
        # Handle candidate addition logic here
    elif message.text == "Админ-панель":
        await message.reply(message_utils.format_admin_panel_message())
        # Handle admin panel logic here
    else:
        await message.reply("Неверный выбор. Пожалуйста, выберите из предложенных вариантов.")

def setup(dp):
    dp.register_message_handler(process_start_command, commands=["start"])
    dp.register_message_handler(process_choose_action, state=StartStates.choose_action)