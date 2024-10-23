import json
import time
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
from db.create_table import CandidatePortrait
from db.create_table import Vacancies
import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from config import DATABASE_URL
from handlers.utils.gpt_for_generate_vacancy import process_commitment


def create_candidate():
    pass
class CandidateInfoStates(StatesGroup):
       waiting_for_title_vacancy = State()
       waiting_for_ideal_candidate = State()
       waiting_for_demographics = State()
       waiting_for_qualities = State()
       waiting_for_skills = State()

cancel = keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ],
            resize_keyboard=True
        )
# 3.  Функция  для  создания  соединения  с  PostgreSQL:**
# async def get_db():
#     async_engine = create_async_engine(DATABASE_URL, echo=True)  # Echo=True для вывода SQL-запросов
#     async_session = async_sessionmaker(
#         async_engine, expire_on_commit=False, class_=AsyncSession
#     )
#     # async with async_session() as session:
#     yield async_session #session
def get_db():
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# 4.  Функция  для  сохранения  информации  о  кандидате  в  базу:**
# async def save_candidate_info(data: Dict[str, Any]):
#     """Сохраняет информацию о кандидате в базу данных."""
#     async with get_db() as session:
#         # Работа с базой данных внутри контекста сессии
#         title_vacancy = data["waiting_for_title_vacancy"]
#         vacancy = await session.execute(
#             """
#             SELECT id FROM vacancies WHERE title = :title_vacancy
#             """,
#             {"title": title_vacancy},
#         )
#         id_vacancy = vacancy.fetchone()
#         if id_vacancy:
#             new_candidate_portrait = CandidatePortrait(vacancy_id=id_vacancy[0], ideal_candidate=data["waiting_for_ideal_candidate"], demographics=data['waiting_for_demographics'], qualities=data["waiting_for_qualities"], skills=data["waiting_for_skills"])
#             session.add(new_candidate_portrait)
#             await session.commit()
#         else:
#             print('id of vacancy not found')
            # await message.reply("Какими должны быть пол, возраст, минимальный опыт?", reply_markup=cancel)
# 

def save_candidate_info(data: dict):
    """Сохраняет информацию о кандидате в базу данных."""
    session = get_db()

    try:
        title_vacancy = data["waiting_for_title_vacancy"]
        vacancy = session.query(Vacancies).filter_by(title=title_vacancy).first()

        if vacancy:
            # Проверяем, существует ли уже портрет кандидата для этой вакансии
            existing_candidate_portrait = session.query(CandidatePortrait).filter_by(vacancy_id=vacancy.id).first()

            if existing_candidate_portrait:
                # Если портрет кандидата уже существует, обновляем его
                existing_candidate_portrait.ideal_candidate = data["waiting_for_ideal_candidate"]
                existing_candidate_portrait.demographics = data["waiting_for_demographics"]
                existing_candidate_portrait.qualities = data["waiting_for_qualities"]
                existing_candidate_portrait.skills = data["waiting_for_skills"]
                session.commit()
                print(f"Портрет кандидата для вакансии '{title_vacancy}' обновлен в базе.")
            else:
                # Если портрета кандидата для этой вакансии нет, создаем новый
                new_candidate_portrait = CandidatePortrait(
                    vacancy_id=vacancy.id,
                    ideal_candidate=data["waiting_for_ideal_candidate"],
                    demographics=data["waiting_for_demographics"],
                    qualities=data["waiting_for_qualities"],
                    skills=data["waiting_for_skills"],
                )
                session.add(new_candidate_portrait)
                session.commit()
                print(f"Портрет кандидата для вакансии '{title_vacancy}' создан в базе.")
        else:
            print(f"Вакансия с названием '{title_vacancy}' не найдена.")

    except Exception as e:
        session.rollback()
        print(f"Ошибка сохранения информации о кандидате: {e}")

    finally:
        session.close()


# async def update_vacancy_description(title: str, description: str):
#     async with get_db() as session:
#         # Используем UPDATE для изменения записи в таблице
#         await session.execute(
#             """
#             UPDATE vacancies
#             SET description = :description
#             WHERE title = :title
#             """,
#             {"description": description, "title": title},
#         )
#         await session.commit()
async def update_vacancy_description(title: str, description: str):
    print('переход к update_vacancy_description')
    session = get_db()
    vacancy = session.query(Vacancies).filter_by(title=title).first()
    if vacancy:
        vacancy.description = description
        session.commit()
    else:
        print("Вакансия с таким названием не найдена")

        
async def get_vacancy_and_portrait_by_title(title: str):
        session = get_db()
        vacancy = session.execute(
            text("""
                SELECT v.*, cp.*
                FROM vacancies v
                JOIN candidate_portrait cp ON v.id = cp.vacancy_id
                WHERE v.title = :title
            """),
            {"title": title},
        )
        result = vacancy.fetchone()
        if result:
            vacancy_data = {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "conditions": result[3],
                "requirements": result[4],
                "responsibilities": result[5],
                "interview_questions": result[6],
                "priority": result[7],
                "ideal_candidate": result[9],  # Индекс 9 для "ideal_candidate"
                "demographics": result[10],  # Индекс 10 для "demographics"
                "qualities": result[11],  # Индекс 11 для "qualities"
                "skills": result[12],  # Индекс 12 для "skills"
            }
            return json.dumps(vacancy_data)  # Преобразование в JSON
        else:
            return None       

# def get_vacancy_and_portrait_by_title(title: str):
#     vacancy = session.query(Vacancies).filter_by(title=title).first()
#     if vacancy:
#         # Используйте relationship для доступа к связанным данным
#         candidate_portrait = vacancy.candidate_portrait
#         if candidate_portrait:
#             vacancy_data = {
#                 "id": vacancy.id,
#                 "title": vacancy.title,
#                 "description": vacancy.description,
#                 "conditions": vacancy.conditions,
#                 "requirements": vacancy.requirements,
#                 "responsibilities": vacancy.responsibilities,
#                 "interview_questions": vacancy.interview_questions,
#                 "priority": vacancy.priority,
#                 "ideal_candidate": candidate_portrait.ideal_candidate,
#                 "demographics": candidate_portrait.demographics,
#                 "qualities": candidate_portrait.qualities,
#                 "skills": candidate_portrait.skills,
#             }
#             return json.dumps(vacancy_data)
#         else:
#             print("Портрет кандидата для этой вакансии не найден")
#             return None
    # else:
    #     print("Вакансия с таким названием не найдена")
    #     return None
    
async def generate_vacancy_by_ai(message: types.Message, title):
    """Генерирует вакансию с помощью AI."""
    data_of_vacancy = await get_vacancy_and_portrait_by_title(title)
    print('!!!в generate_vacancy_by_ai', data_of_vacancy)
    prompt = 'напиши текст вакансии по следующим данным: ' + data_of_vacancy 
    vacancy = await process_commitment(message, prompt)
    await update_vacancy_description(title, vacancy)
    await message.answer(vacancy)

# 5.  Функция  для  сбора  информации  о  кандидате:
async def collect_candidate_portrait_info(message: types.Message, state: FSMContext):
    print("in collect_candidate_info")
    if await state.get_state() == CandidateInfoStates.waiting_for_ideal_candidate:
        await state.update_data(waiting_for_ideal_candidate=message.text)
        await state.set_state(CandidateInfoStates.waiting_for_demographics)
        await message.reply("Какими должны быть пол, возраст, минимальный опыт?", reply_markup=cancel)
    elif await state.get_state() == CandidateInfoStates.waiting_for_demographics:
        # data["demographics"] = message.text
        await state.update_data(waiting_for_demographics=message.text)
        # await message.reply("Какие у него должны быть качества?")
        await state.set_state(CandidateInfoStates.waiting_for_qualities)
        await message.reply("Какие у него должны быть качества?", reply_markup=cancel)
    elif await state.get_state() == CandidateInfoStates.waiting_for_qualities:
        # data["qualities"] = message.text
        await state.update_data(waiting_for_qualities=message.text)
        await state.set_state(CandidateInfoStates.waiting_for_skills)
        await message.reply("Какими навыками должен обладать?", reply_markup=cancel)
    elif await state.get_state() == CandidateInfoStates.waiting_for_skills:
        # data["skills"] = message.text
        await state.update_data(waiting_for_skills=message.text)
        data = await state.get_data()
        save_candidate_info(data=data)
        await message.reply("Информация о кандидате собрана!")
        await show_summary(message=message, data=data)
        if title:=data[' _vacancy']:
            print('переход к генерации вакансии...', data)
            vacancy = await generate_vacancy_by_ai(message, title)
            # update_vacancy_description(title, vacancy)
        await state.clear()
    # return ideal_candidate, demographics, qualities, skills
async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    waiting_for_ideal_candidate = data["waiting_for_ideal_candidate"]
    waiting_for_demographics = data['waiting_for_demographics']
    waiting_for_qualities = data['waiting_for_qualities']
    waiting_for_skills = data['waiting_for_skills']
    await message.answer(f"{waiting_for_ideal_candidate}\n\n{waiting_for_demographics}\n\n{waiting_for_qualities}\n\n{waiting_for_skills}", reply_markup=ReplyKeyboardRemove())
# 6.  Регистрация  обработчиков  сообщений:**
