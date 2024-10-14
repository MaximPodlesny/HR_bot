from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict, Optional, List

from db.models import Vacancy, Candidate
from bot.config import DATABASE_URL

engine = create_engine(DATABASE_URL)  
Session = sessionmaker(bind=engine)
session = Session()

async def save_vacancy(vacancy: Vacancy) -> int:
    """
    Saves a new vacancy to the database.
    """
    session.add(vacancy)
    session.commit()
    return vacancy.id

async def update_vacancy(vacancy_id: int, vacancy_data: Dict) -> bool:
    """
    Updates an existing vacancy in the database.
    """
    vacancy = session.query(Vacancy).filter_by(id=vacancy_id).first()
    if vacancy:
        for key, value in vacancy_data.items():
            setattr(vacancy, key, value)
        session.commit()
        return True
    else:
        return False

async def delete_vacancy(vacancy_id: int) -> bool:
    """
    Deletes a vacancy from the database.
    """
    vacancy = session.query(Vacancy).filter_by(id=vacancy_id).first()
    if vacancy:
        session.delete(vacancy)
        session.commit()
        return True
    else:
        return False

async def save_candidate(candidate: Candidate) -> int:
    """
    Saves a new candidate to the database.
    """
    session.add(candidate)
    session.commit()
    return candidate.id

async def update_candidate(candidate_id: int, candidate_data: Dict) -> bool:
    """
    Updates an existing candidate in the database.
    """
    candidate = session.query(Candidate).filter_by(id=candidate_id).first()
    if candidate:
        for key, value in candidate_data.items():
            setattr(candidate, key, value)
        session.commit()
        return True
    else:
        return False

async def delete_candidate(candidate_id: int) -> bool:
    """
    Deletes a candidate from the database.
    """
    candidate = session.query(Candidate).filter_by(id=candidate_id).first()
    if candidate:
        session.delete(candidate)
        session.commit()
        return True
    else:
        return False

async def get_vacancy(vacancy_id: int) -> Optional[Vacancy]:
    """
    Retrieves a vacancy from the database.
    """
    return session.query(Vacancy).filter_by(id=vacancy_id).first()

async def get_candidate(candidate_id: int) -> Optional[Candidate]:
    """
    Retrieves a candidate from the database.
    """
    return session.query(Candidate).filter_by(id=candidate_id).first()

async def get_candidates_by_vacancy(vacancy_id: int) -> List[Candidate]:
    """
    Retrieves all candidates for a specific vacancy.
    """
    return session.query(Candidate).filter_by(vacancy_id=vacancy_id).all()