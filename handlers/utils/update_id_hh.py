import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from db.create_table import Vacancies, Candidates
from config import DATABASE_URL
from handlers.utils.candidate import get_db

async def update_id_hh_by_title(title: str, id_hh: int):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    vacancy = session.query(Vacancies).filter_by(title=title).first()
    if vacancy:
        vacancy.id_hh = id_hh
        session.commit()
    else:
        print("Кандидат не найден")