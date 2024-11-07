import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from db.create_table import Vacancies, Candidates
from config import DATABASE_URL
from handlers.utils.candidate import get_db

async def update_telegram_id_by_candidate_id(u_id: str, t_id: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(id=u_id).first()
    if candidate:
        candidate.telegram_id = t_id
        session.commit()
    else:
        print("Кандидат не найден")


async def update_fio_by_candidate_id(u_id: str, t_id: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(id=u_id).first()
    if candidate:
        candidate.telegram_id = t_id
        session.commit()
    else:
        print("Кандидат не найден")

async def new_candidate(fio: str, t_id: str):
    print('переход к new_candidate')
    session = get_db()
    # Создаем нового кандидата
    candidate = Candidates(
        fio=fio,
        telegram_id=t_id,
        phone_number="",
        vacancy_id=0,  # Замените на ID вакансии
        first_interview_questions="",
        second_interview_questions="",
        test_task="",
)
    session.add(candidate)
    session.commit()
    if candidate:
        print("Кандидат создан")
    else:
        print("Кандидат не создан")

async def update_first_interview_by_candidate_id(t_id: str, first_interview_aqnswer: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=t_id).first()
    if candidate:
        candidate.first_interview_questions = first_interview_aqnswer
        session.commit()
    else:
        print("Кандидат не найден")

async def update_second_interview_by_candidate_id(t_id: str, first_interview_aqnswer: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=t_id).first()
    if candidate:
        candidate.first_interview_questions = first_interview_aqnswer
        session.commit()
    else:
        print("Кандидат не найден")
