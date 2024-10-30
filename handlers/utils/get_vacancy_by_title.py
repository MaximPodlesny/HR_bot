from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import sessionmaker

from db.create_table import Vacancies

from .candidate import get_db

async def get_vacancy(title):
    session = get_db()
    vacancy = session.query(Vacancies).filter_by(title=title).first()
    return vacancy