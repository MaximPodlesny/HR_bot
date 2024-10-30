from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import sessionmaker

from db.create_table import Vacancies

from .candidate import get_db

async def get_vacancies():
    session = get_db()
    vacancies = session.query(Vacancies).all()
    session.close()
    return vacancies