from sqlalchemy import create_engine
from .models import Base, Vacancy, Candidate
from bot.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)