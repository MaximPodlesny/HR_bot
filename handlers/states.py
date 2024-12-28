from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup


class DocumentInfoStates(StatesGroup):
       waiting_for_id_document = State()
       waiting_for_name_document = State()
       waiting_for_data_of_resumes = State()

class UserchatInfoStates(StatesGroup):
       admin_ids = State()
       name_of_user = State()
       chosen_vacancy = State()
       list_vacancies = State()
       waiting_for_questions = State()

class CreateVacancyInfoStates(StatesGroup):
       create_vacancy = State()
       # description = State()
       # sity_id = State()
       # role = State()
       # info_from_vacancy = State()
       # (message, state, title_of_vacancy, description, sity_id, role, info_from_vacancy)