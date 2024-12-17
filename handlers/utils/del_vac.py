from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import sessionmaker

from db.create_table import Vacancies

from .candidate import get_db

async def del_vacancy(title):
    session = get_db()
    try:
        vacancy = session.query(Vacancies).filter_by(title=title).first()
        if vacancy:
            session.delete(vacancy)
            session.commit()
            print(f"Запись с названием '{title}' удалена.")
        else:
            print(f"Запись с названием '{title}' не найдена.")
    except:
        return None
    finally:
        session.close()
