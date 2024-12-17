import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from db.create_table import Vacancies, Candidates
from config import DATABASE_URL
from handlers.utils.candidate import get_db

async def update_telegram_id_by_candidate_id(u_id: str, t_id: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(id=u_id).first()
    if candidate:
        candidate.telegram_id = t_id
        session.commit()
    else:
        print("Кандидат не найден")


async def update_fio_by_candidate_id(u_id: str, t_id: str):
    print('переход к update_telegram_id_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(id=u_id).first()
    if candidate:
        candidate.telegram_id = t_id
        session.commit()
    else:
        print("Кандидат не найден")

async def new_candidate(candidate_id: int, fio: str, t_id: str, title_of_vacancy):
    print('переход к new_candidate')
    session = get_db()
    try:
        candidate = session.query(Candidates).filter_by(id=candidate_id).first()
    except:
        pass
    if candidate_id is None or not candidate:
        # Создаем нового кандидата
        candidate = Candidates(
            fio=fio,
            telegram_id=t_id,
            phone_number="",
            # vacancy_id=0,  # Замените на ID вакансии
            first_interview_questions="",
            second_interview_questions="",
            test_task="",
            title_of_vacancy=title_of_vacancy
    )
    else:
        candidate.fio = fio
        candidate.telegram_id = t_id
        candidate.title_of_vacancy = title_of_vacancy
    session.add(candidate)
    session.commit()


async def update_first_interview_by_candidate_id(t_id: str, first_interview_aqnswer: str):
    print('переход к update_first_interview_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=str(t_id)).first()
    if candidate:
        candidate.first_interview_questions = first_interview_aqnswer
        session.commit()
    else:
        print("Кандидат не найден")

async def update_second_interview_by_candidate_id(t_id: str, first_interview_aqnswer: str):
    print('переход к update_second_interview_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=str(t_id)).first()
    if candidate:
        candidate.first_interview_questions = first_interview_aqnswer
        session.commit()
    else:
        print("Кандидат не найден")

async def update_time_test_task_by_candidate_id(t_id: str, cur_time: str=False, end_time=False):
    print('переход к update_time_test_task_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=str(t_id)).first()
    if candidate and end_time is False:
        time_for_test = {'start_time': cur_time, 'end_time': 0}
        candidate.time_test_task = time_for_test
        session.commit()

    elif candidate and end_time != False:
        time_for_test = candidate.time_test_task
        time_for_test['end_time'] = end_time
        candidate.time_test_task = time_for_test
        session.commit()
        return time_for_test
    else:
        print("Кандидат не найден")

async def time_for_test_task_by_candidate_id(t_id: str):
    print('переход к update_time_test_task_by_candidate_id')
    session = get_db()
    candidate = session.query(Candidates).filter_by(telegram_id=str(t_id)).first()
    title_vacancy = candidate.title_of_vacancy
    vacancy = session.query(Vacancies).filter_by(title=title_vacancy).first()
    time_for_test = int(''.join(i for i in vacancy.test_task['time_to_complete'] if i.isdigit()))
    return time_for_test
