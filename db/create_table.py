from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from alembic import context
from config import DATABASE_URL

# try:
engine = create_engine(DATABASE_URL.replace("'", "") , echo=True)  # Echo=True для вывода SQL-запросов

# except:
# print("Ошибка подключения к базе данных")
# Session = sessionmaker(bind=engine)
# session = Session()
Base = declarative_base()

# Определение таблиц с помощью SQLAlchemy
  
class Candidates(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    fio = Column(String)
    telegram_id = Column(String)
    phone_number = Column(String)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), unique=True)
    first_interview_questions = Column(String)
    second_interview_questions = Column(String)
    test_task = Column(String)
    title_of_vacancy = Column(String)

    vacancy = relationship("Vacancies", back_populates="candidates") # Добавили relationship
class Vacancies(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True)
    id_hh= Column(Integer)
    title = Column(String)
    description = Column(String)
    conditions = Column(String)
    requirements = Column(String)
    responsibilities = Column(String)
    interview_questions = Column(String)
    priority = Column(String)
    test_task = Column(String)

    candidates = relationship("Candidates", back_populates="vacancy", cascade="all, delete-orphan") # Вот строка с каскадом
    candidate_portrait = relationship("CandidatePortrait", back_populates="vacancy", cascade="all, delete-orphan", uselist = False) # Вот строка с каскадом
class CandidatePortrait(Base):
    __tablename__ = "candidate_portrait"
    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), unique=True)
    ideal_candidate = Column(String)
    demographics = Column(String)
    qualities = Column(String)
    skills = Column(String)

    vacancy = relationship("Vacancies", back_populates="candidate_portrait") # Добавили relationship
class AdminPenal(Base):
    __tablename__ = "admin_penal"
    id = Column(Integer, primary_key=True)
    admin_ids = Column(String)


# Создание таблиц в базе данных

def create_tables():
    Base.metadata.create_all(engine)

# Создание сессии для взаимодействия с базой данных

Session = sessionmaker(bind=engine)
session = Session()

# Пример использования сессии для вставки данных

# new_vacancy = Vacancies(
#     title="Python Developer",
#     description="..."
# )
# session.add(new_vacancy)
# session.commit()

# new_candidate = Candidates(
#     fio="Иван Иванов",
#     telegram_id=123456789,
#     phone_number="+79991234567",
#     vacancy_id=new_vacancy.id  # Связь с вакансией
# )
# session.add(new_candidate)
# session.commit()

# new_candidate_portrait = CandidatePortrait(
#     vacancy_id=new_vacancy.id,
#     ideal_candidate="...",
#     demographics="...",
#     qualities="...",
#     skills="..."
# )
# session.add(new_candidate_portrait)
# session.commit()


if __name__ == "__main__":
    create_tables()
