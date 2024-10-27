import json
from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
from openai import AsyncOpenAI

from config import GPT_KEY
from db.create_table import Vacancies
from handlers.utils.chat_history import ChatHistory
from handlers.utils.get_history_by_user_id import get_history_by_user_id
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils.gpt_for_generate_vacancy import process_commitment
# from aiogram.dispatcher.filters import ContentTypesFilter
# from bot import bot
from .search_candidate import search_c
from handlers.utils.candidate import CandidateInfoStates, collect_candidate_portrait_info, get_db, save_candidate_info, update_vacancy_description
from .create_vacancy import VacancyInfoStates, collect_vacancy_info, save_vacancy_info
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup

router = Router()

# обработчик отправки файла
@router.message(F.document)
async def handle_file(message: types.Message):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        # await message.reply(f"Получен файл: {file_name}")
        # await bot.send_document(chat_id=message.chat.id, document=file_id, caption="Загруженный файл")
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    # types.KeyboardButton(text="Сохранить тестовое задание"),
                    types.KeyboardButton(text="Поиск кандидата"),
                ],
                [
                    types.KeyboardButton(text="Сохранить тестовое задание"),
                ]
            ],
            resize_keyboard=True
        )
        await message.answer(f"Получен файл: {file_name}! Что с ним сделать?", reply_markup=keyboard)