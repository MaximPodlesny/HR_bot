import os
import asyncio
from typing import Any, Dict

from aiogram import Bot, Dispatcher, types
# from aiogram.dispatcher import FSMContext
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
# from aiogram.utils import executor
# from aiogram.utils.markdown import hbold, hcode
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from openai import OpenAI
import psycopg2

# from handlers.handlers import CandidateInfoStates


def create_candidate():
    pass
class CandidateInfoStates(StatesGroup):
       waiting_for_ideal_candidate = State()
       waiting_for_demographics = State()
       waiting_for_qualities = State()
       waiting_for_skills = State()


# 3.  Функция  для  создания  соединения  с  PostgreSQL:**
async def get_db_connection():
    """Создает соединение с базой данных PostgreSQL."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# 4.  Функция  для  сохранения  информации  о  кандидате  в  базу:**
async def save_candidate_info(chat_id: int, candidate_info: Dict):
    """Сохраняет информацию о кандидате в базу данных."""
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO candidates (chat_id, ideal_candidate, demographics, qualities, skills)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (chat_id, candidate_info["ideal_candidate"], candidate_info["demographics"], candidate_info["qualities"], candidate_info["skills"]),
            )
            conn.commit()

# 5.  Функция  для  сбора  информации  о  кандидате:
async def collect_candidate_info(message: types.Message, state: FSMContext):
    print("in collect_candidate_info-{} /n {}".format(await state.get_state(), CandidateInfoStates.waiting_for_ideal_candidate))
    if await state.get_state() == CandidateInfoStates.waiting_for_ideal_candidate:
        await state.update_data(waiting_for_ideal_candidate=message.text)
        # data["ideal_candidate"] = message.text
        await message.reply("Какими должны быть пол, возраст, минимальный опыт?")
        await state.set_state(CandidateInfoStates.waiting_for_demographics)
    elif await state.get_state() == CandidateInfoStates.waiting_for_demographics:
        # data["demographics"] = message.text
        await state.update_data(waiting_for_demographics=message.text)
        await message.reply("Какие у него должны быть качества?")
        await state.set_state(CandidateInfoStates.waiting_for_qualities)
    elif await state.get_state() == CandidateInfoStates.waiting_for_qualities:
        # data["qualities"] = message.text
        await state.update_data(waiting_for_qualities=message.text)
        await message.reply("Какими навыками должен обладать?")
        await state.set_state(CandidateInfoStates.waiting_for_skills)
    elif await state.get_state() == CandidateInfoStates.waiting_for_skills:
        # data["skills"] = message.text
        data = await state.update_data(waiting_for_skills=message.text)
        await message.reply("Информация о кандидате собрана!")
        # await save_candidate_info(message.chat.id, data)
        # ideal_candidate = data['ideal_candidate']
        # demographics = data['demographics']
        # qualities = data['qualities']
        # skills = data['skills']
        await show_summary(message=message, data=data)

        # # Вывод информации в консоль
        # print(f"Собрана информация о кандидате:")
        # print(f"Идеальный кандидат: {data['ideal_candidate']}")
        # print(f"Демографические данные: {data['demographics']}")
        # print(f"Качества: {data['qualities']}")
        # print(f"Навыки: {data['skills']}")
        await state.clear()
    # return ideal_candidate, demographics, qualities, skills
async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    waiting_for_ideal_candidate = data["waiting_for_ideal_candidate"]
    waiting_for_demographics = data['waiting_for_demographics']
    waiting_for_qualities = data['waiting_for_qualities']
    waiting_for_skills = data['waiting_for_skills']
    await message.answer(f"{waiting_for_ideal_candidate}\n\n{waiting_for_demographics}\n\n{waiting_for_qualities}\n\n{waiting_for_skills}", reply_markup=ReplyKeyboardRemove())
# 6.  Регистрация  обработчиков  сообщений:**
