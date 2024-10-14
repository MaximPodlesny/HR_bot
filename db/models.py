from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    interview_questions = Column(Text)
    priority_criteria = Column(Text)
    status = Column(String, default="open")  # "open", "closed", etc.

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"))
    name = Column(String)
    telegram_id = Column(Integer)
    hh_profile_url = Column(String)
    resume_file = Column(String)
    status = Column(String, default="applied")  # "applied", "interviewed", "rejected", "hired", etc.
    interview_answers = Column(Text)
    test_task_file = Column(String)
    notes = Column(Text)