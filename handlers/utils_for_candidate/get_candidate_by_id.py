from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import sessionmaker

from db.create_table import Candidates

from ..utils.candidate import get_db

async def get_candidate(id):
    session = get_db()
    candidate = session.query(Candidates).filter_by(id=id).first()
    session.close()
    return candidate