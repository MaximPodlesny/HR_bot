from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
# 1. Подключение к базе данных
engine = create_engine(DATABASE_URL)  # Замените на ваши данные
metadata = MetaData()

# 2. Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# 3. Очистка таблиц
try:
    # Очистка таблицы "Таблица1"
    session.execute(text("TRUNCATE TABLE candidates RESTART IDENTITY CASCADE"))

    # Очистка таблицы "Таблица2"
    session.execute(text("TRUNCATE TABLE candidate_portrait RESTART IDENTITY CASCADE"))

    # Очистка таблицы "Таблица3"
    session.execute(text("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE"))

    session.commit()
    print("Таблицы успешно очищены!")
except Exception as e:
    session.rollback()
    print(f"Ошибка очистки таблиц: {e}")

session.close()
engine.dispose()