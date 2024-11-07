import logging
from typing import Any, Dict
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from db.create_table import Vacancies
import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from .utils.candidate import CandidateInfoStates

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



logging.basicConfig(level=logging.INFO)
keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ],
            resize_keyboard=True
        )

class VacancyInfoStates(StatesGroup):
    waiting_for_create_portrait = State()
    waiting_for_title_vacancy = State()
    waiting_for_conditions = State()
    waiting_for_requirements = State()
    waiting_for_responsibilities = State()
    waiting_for_interview_questions = State()
    waiting_for_priority = State()

# 3.  Функция  для  создания  соединения  с  PostgreSQL:**
def get_db():
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def save_vacancy_info(data: dict):
    """Сохраняет информацию о вакансии в базу данных."""
    session = get_db()  # Получаем сессию с базой данных
    
    # Проверяем, существует ли вакансия с таким же названием в базе
    title = data["waiting_for_title_vacancy"]
    existing_vacancy = session.query(Vacancies).filter_by(title=title).first()
    
    if existing_vacancy:
        # Если вакансия уже существует, обновляем ее
        existing_vacancy.conditions = data["waiting_for_conditions"]
        existing_vacancy.requirements = data["waiting_for_requirements"]
        existing_vacancy.responsibilities = data["waiting_for_responsibilities"]
        existing_vacancy.interview_questions = data["waiting_for_interview_questions"]
        existing_vacancy.priority = data["waiting_for_priority"]
        session.commit()
        print(f"Вакансия с названием '{title}' сохранена в базу.")
    else:
        # Если вакансии с таким названием нет, просто сохраняем новую
        new_vacancy = Vacancies(
            title=data["waiting_for_title_vacancy"],
            conditions=data["waiting_for_conditions"],
            requirements=data["waiting_for_requirements"],
            responsibilities=data["waiting_for_responsibilities"],
            interview_questions=data["waiting_for_interview_questions"],
            priority=data["waiting_for_priority"],
        )
        session.add(new_vacancy)
        session.commit()
        print(f"Вакансия с названием '{title}' сохранена в базу.")

# 5.  Функция  для  сбора  информации  о  кандидате:
async def collect_vacancy_info(message: types.Message, state: FSMContext):
    print(
        "in collect_vacancy_info"
    )
    global keyboard
    if await state.get_state() == VacancyInfoStates.waiting_for_title_vacancy:
        await state.update_data(waiting_for_title_vacancy=message.text) # (waiting_for_conditions=message.text)
        await state.set_state(VacancyInfoStates.waiting_for_conditions)
        await message.reply("Опишите условия работы: график, зп, удаленно/офлайн, бонусы, KPI?", reply_markup=keyboard)
    elif await state.get_state() == VacancyInfoStates.waiting_for_conditions:
        await state.update_data(waiting_for_conditions=message.text)
        await state.set_state(VacancyInfoStates.waiting_for_requirements)
        await message.reply("Какие требования к кандидату?", reply_markup=keyboard)
    elif await state.get_state() == VacancyInfoStates.waiting_for_requirements:
        await state.update_data(waiting_for_requirements=message.text)
        await state.set_state(VacancyInfoStates.waiting_for_responsibilities)
        await message.reply("Какие обязанности будут у кандидата?", reply_markup=keyboard)
    elif await state.get_state() == VacancyInfoStates.waiting_for_responsibilities:
        await state.update_data(waiting_for_responsibilities=message.text)
        await message.reply("Какие вопросы зададите на собеседовании?")
        await state.set_state(VacancyInfoStates.waiting_for_interview_questions)
        # await message.reply("Какие обязанности будут у кандидата?", reply_markup=keyboard)
    elif await state.get_state() == VacancyInfoStates.waiting_for_interview_questions:
        await state.update_data(waiting_for_interview_questions=message.text)
        await state.set_state(VacancyInfoStates.waiting_for_priority)
        await message.reply("На что вы будете обращать внимание при финальном выборе?", reply_markup=keyboard)
    elif (await state.get_state() == VacancyInfoStates.waiting_for_priority) and ((await state.get_data())["waiting_for_create_portrait"] != 'создать'):
        await state.update_data(waiting_for_priority=message.text)
        data = await state.get_data()
        await message.reply("Информация о вакансии собрана!")
        save_vacancy_info(data=data)
        # await save_candidate_info(message.chat.id, data)
        await show_summary(message=message, data=data)
        await state.clear()
    elif (await state.get_state() == VacancyInfoStates.waiting_for_priority) and ((await state.get_data())["waiting_for_create_portrait"] == 'создать'):
        await state.update_data(waiting_for_priority=message.text)
        data = await state.get_data()
        save_vacancy_info(data=data)
        await message.reply("Информация о вакансии собрана!")
        await show_summary(message=message, data=data)
        await message.answer('Хорошо! Давайте соберем информацию о кандидате.')
        await state.set_state(CandidateInfoStates.waiting_for_ideal_candidate)
        await state.update_data(waiting_for_title_vacancy=data["waiting_for_title_vacancy"])
        await state.set_state(CandidateInfoStates.waiting_for_ideal_candidate)
        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        types.KeyboardButton(text="Отмена"),
                    ],
                ], 
                resize_keyboard=True
        )
        await message.reply('Каким вы видите идеального кандидата?', reply_markup=keyboard)
        
        # await save_candidate_info(message.chat.id, data)
        
        

async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    waiting_for_title_vacancy = data["waiting_for_title_vacancy"]
    waiting_for_conditions = data["waiting_for_conditions"]
    waiting_for_requirements = data["waiting_for_requirements"]
    waiting_for_responsibilities = data["waiting_for_responsibilities"]
    waiting_for_interview_questions = data["waiting_for_interview_questions"]
    waiting_for_priority = data["waiting_for_priority"]
    await message.answer(
        f"Название вакансии: {waiting_for_title_vacancy}\n\n"
        f"Условия работы: {waiting_for_conditions}\n\n"
        f"Требования: {waiting_for_requirements}\n\n"
        f"Обязанности: {waiting_for_responsibilities}\n\n"
        f"Вопросы на собеседовании: {waiting_for_interview_questions}\n\n"
        f"Приоритет: {waiting_for_priority}",
        reply_markup=ReplyKeyboardRemove(),
    )
