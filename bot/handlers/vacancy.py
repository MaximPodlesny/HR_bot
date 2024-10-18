from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import hh_api, openai_utils, db_utils, message_utils
from db.models import Vacancy

class VacancyStates(StatesGroup):
    collecting_info = State()
    confirming_vacancy = State()

async def collect_vacancy_info(message: types.Message, state: FSMContext):
    """Collects vacancy information from the user."""
    async with state.proxy() as data:
        vacancy_data = data.get("vacancy_data", {})
        # Implement logic to extract vacancy details from the message text
        # Use OpenAI to suggest missing fields
        vacancy_data.update(extracted_info)
        data["vacancy_data"] = vacancy_data
    await message.reply(message_utils.format_vacancy_data(vacancy_data))
    await message.reply("Подтвердить создание вакансии? Да/Нет")
    await state.set_state(VacancyStates.confirming_vacancy.state)

async def confirm_vacancy_creation(message: types.Message, state: FSMContext):
    """Confirms and creates the vacancy in the database."""
    if message.text.lower() == "да":
        async with state.proxy() as data:
            vacancy_data = data.get("vacancy_data")
        vacancy = Vacancy(**vacancy_data)
        await db_utils.save_vacancy(vacancy)
        await message.reply(f"Вакансия {vacancy.title} успешно создана!")
        await state.finish()
    elif message.text.lower() == "нет":
        await message.reply("Создание вакансии отменено.")
        await state.finish()
    else:
        await message.reply("Неверный ввод. Введите Да или Нет.")

async def publish_vacancy_on_hh(message: types.Message, state: FSMContext):
    """Publishes a vacancy on HH.ru."""
    async with state.proxy() as data:
        vacancy_data = data.get("vacancy_data")
    await hh_api.publish_vacancy(vacancy_data)
    await message.reply(f"Вакансия {vacancy_data['title']} успешно опубликована на HH.ru!")
    await state.finish()

def setup(dp):
    dp.register_message_handler(collect_vacancy_info, state=VacancyStates.collecting_info)
    dp.register_message_handler(confirm_vacancy_creation, state=VacancyStates.confirming_vacancy)
    dp.register_message_handler(publish_vacancy_on_hh, commands=["publish_hh"]) 