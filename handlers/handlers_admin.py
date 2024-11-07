import json
from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
from openai import AsyncOpenAI

from config import GPT_KEY, ADMIN
from db.create_table import Vacancies
from handlers.utils.chat_history import ChatHistory
from handlers.utils.get_history_by_user_id import get_history_by_user_id
from handlers.utils.gpt_for_analise_resumes import ResumesInfoStates, search_good_resumes
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils.gpt_for_generate_vacancy import process_commitment
from handlers.utils.parser_pdf import parser
from handlers.utils.send_invite_by_whatsapp import send_mes_whatsapp
# from aiogram.dispatcher.filters import ContentTypesFilter
# from bot import bot
from .search_candidate import search_c
from handlers.utils.candidate import CandidateInfoStates, collect_candidate_portrait_info, get_db, save_candidate_info, update_vacancy_description
from .create_vacancy import VacancyInfoStates, collect_vacancy_info, save_vacancy_info
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup

router = Router()

class DocumentInfoStates(StatesGroup):
       waiting_for_id_document = State()
       waiting_for_name_document = State()
       waiting_for_data_of_resumes = State()

# Обработчик ответа Cancel
@router.message((F.text == "Отмена") & (F.from_user.id == ADMIN))
async def process_hh(message: types.Message):
    print('in cancel admin')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Найти кандидата"),
                types.KeyboardButton(text="Создать вакансию"),
            ],
        ],
        resize_keyboard=True
    )
    await message.answer("Хорошо! Выберите, что будем делать дальше:", reply_markup=keyboard)

# Если есть портрет кандидата
@router.message((F.text == "Нет портрета") & (F.from_user.id == ADMIN))
async def find_candidate(message: types.Message, state: FSMContext):
    print('in Нет портрета admin')
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ],
            resize_keyboard=True
        )
    await message.reply("Напишите название вакансии.", reply_markup=keyboard)
    await state.set_state(VacancyInfoStates.waiting_for_title_vacancy)
    await state.update_data(waiting_for_create_portrait='создать')

# Обработчик ответа "ДА"
@router.message((F.text == "Найти кандидата") & (F.from_user.id == ADMIN))
async def find_candidate(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="через hh"),
                types.KeyboardButton(text="собственная база"),
            ],
        ],
        resize_keyboard=True
    )
    await message.answer("Хорошо! Мы будем искать кандидатов по загруженной информации или через HH ?", reply_markup=keyboard)

# Обработчик создания вакансии
@router.message((F.text.in_(["Создать вакансию","К созданию вакансии", "через hh"])) & (F.from_user.id == ADMIN))
async def process_hh(message: types.Message, state: FSMContext):
    await message.answer("Нам нужна будет следующяя информация:\
        \
        Название вакансии.\
        \
        Портрет Кандидата:\
        \
        *   Пол / Возраст:  Укажите  желаемый  пол  и  возраст  кандидата.\
        *   Личные  качества:  Опишите  минимум  два  важных  для  вас  личных  качества  кандидата.\
        *   Минимальный  опыт:  Укажите  минимальный  опыт  работы,  который  требуется  для  этой  вакансии.\
        \
        Условия:\
        \
        *   График  работы:  Укажите  желаемый  график  работы  (полный  день,  неполный  день,  гибкий  график  и  т.д.).\
        *   Заработная  плата:  Укажите  желаемую  заработную  плату.\
        *   Удаленная  работа / Офис:  Укажите,  будет  ли  работа  удаленной  или  в  офисе.\
        *   Бонусы:  Укажите,  предусмотрены  ли  бонусы  для  этой  позиции.\
        *   KPI:  Укажите,  будут  ли  использоваться  KPI  для  оценки  работы  кандидата.\
        \
        Требования:\
        \
        *   Качества / Навыки:  Опишите  минимум  два  важных  для  вас  качества  или  навыка  кандидата.\
        \
        Обязанности:\
        \
        *   Задачи:  Перечислите  минимум  две  основные  задачи,  которые  будет  выполнять  кандидат  на  этой  работе.\
        \
        Вопросы  на  интервью:\
        \
        *   Вопросы:  Сформулируйте  минимум  три  вопроса,  которые  вы  будете  задавать  кандидату  на  интервью.\
        *   Идеальные  ответы:  Опишите  желаемые  ответы  на  эти  вопросы.\
        \
        Приоритеты  при  выборе:\
        \
        *   Приоритет:  Укажите,  на  что  вы  будете  обращать  внимание  в  первую  очередь  при  финальном  выборе  кандидата."
    )
    await message.answer('Хорошо! Давайте соберем информацию о вакансии.')
    
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Есть портрет"),
                    types.KeyboardButton(text="Нет портрета"),
                ],
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ],
            resize_keyboard=True
    )
    await message.reply('У Вас уже есть портрет кандидата?', reply_markup=keyboard)
    
@router.message(VacancyInfoStates.waiting_for_title_vacancy)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_vacancy_info(message, state)

@router.message(VacancyInfoStates.waiting_for_conditions)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    print("in look_for_vacancy")
    # await message.answer('Хорошо! Какими должны быть пол, возраст, минимальный опыт?')
    # await state.set_state(CandidateInfoStates.waiting_for_demographics)
    answer = await collect_vacancy_info(message, state)

@router.message(VacancyInfoStates.waiting_for_requirements)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_vacancy_info(message, state)

@router.message(VacancyInfoStates.waiting_for_responsibilities)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_vacancy_info(message, state)

@router.message(VacancyInfoStates.waiting_for_interview_questions)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_vacancy_info(message, state)

@router.message(VacancyInfoStates.waiting_for_priority)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_vacancy_info(message, state)

# Обработчик ответа "собственная база"
@router.message((F.text == "собственная база") & (F.from_user.id == ADMIN))
async def process_my_data(message: types.Message):
    # search_candidate()
    await message.answer("Загрузите резюме(csv) и тестовое задание(txt)")

# Обработчик после получения ботом файла
# @router.message(F.text == "Поиск кандидата" | F.text == "К поиску кандидата")
@router.message((F.text.in_(["Поиск кандидата","К поиску кандидата", "Создать портрет"])) & (F.from_user.id == ADMIN))
async def list_vacancies(message: types.Message, state: FSMContext, data=None):
    await state.set_state(DocumentInfoStates)
    if not data:
        data = await state.get_data()
        list_structured_resumes = await parser(data['waiting_for_id_document'])
    else:
        list_structured_resumes = data['data_of_resumes']
    await state.update_data(waiting_for_data_of_resumes=list_structured_resumes)

    with open("resumes.txt", "w", encoding='utf-8') as f:
        for k, v in enumerate(json.loads(list_structured_resumes).items()):  # json.loads преобразует json в python-объекты 
            print('i - ', v)
            print(f'{v[0]}: {v[1]}', file=f)

    await message.answer('Хорошо! Давайте соберем информацию о кандидате.')
    await state.set_state(CandidateInfoStates.waiting_for_ideal_candidate)
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ], 
            resize_keyboard=True
    )
    await message.reply('Каким вы видите идеального кандидата?', reply_markup=keyboard)
    

@router.message(CandidateInfoStates.waiting_for_ideal_candidate)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    print("in look_for_candidate - waiting_for_ideal_candidate")
    # await message.answer('Хорошо! Какими должны быть пол, возраст, минимальный опыт?')
    # await state.set_state(CandidateInfoStates.waiting_for_demographics)
    answer = await collect_candidate_portrait_info(message, state)

@router.message(CandidateInfoStates.waiting_for_demographics)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_candidate_portrait_info(message, state)

@router.message(CandidateInfoStates.waiting_for_qualities)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_candidate_portrait_info(message, state)

@router.message(CandidateInfoStates.waiting_for_skills)
async def info_for_vacancy(message: types.Message, state: FSMContext):
    answer = await collect_candidate_portrait_info(message, state)

@router.message(CandidateInfoStates.waiting_for_data_of_candidate)
@router.message((F.text == "Искать") & (F.from_user.id == ADMIN))
async def search_vacancies(message: types.Message, state: FSMContext, data=None):
    # data_of_candidate = await state.get_data()
    # print('data_of_candidate - ', data_of_candidate)
    # await state.set_state(DocumentInfoStates)
    if data:
        data_of_resumes = data['data_of_resumes']
    else:
        data = await state.get_data()
        data_of_resumes = data['waiting_for_data_of_resumes']
    data_of_candidate = {
        'идеальный кандидат': data['waiting_for_ideal_candidate'],
        'демографические данные': data['waiting_for_demographics'],
        'качества кандидата': data['waiting_for_qualities'],
        'навыка кандидата': data['waiting_for_skills'],
    }

    
    await search_good_resumes(message, data_of_resumes, data_of_candidate, state)
    # await state.set_state(ResumesInfoStates.waiting_for_list_contact)
    data = await state.get_data()
    data_contacts_for_send = data.get('waiting_for_list_contact', [])
    # print(f'data {data}', f'data_contacts_for_send {data_contacts_for_send} {type(data_contacts_for_send )}')
    contacts = [(t if (t:=str(a).replace(' ', '').replace('(', '').replace(')', '').replace('-', ''))[0] == '+' else f'+7{t[1:]}', str(b)) for a, b in data_contacts_for_send] if data_contacts_for_send else []
    if contacts:
        await send_mes_whatsapp(contacts)
    else:
        await message.answer("К сожалению, нам не удалось найти подходящего кандидата.")
        
# @router.message(CandidateInfoStates.waiting_for_data_of_candidate)
# @router.message(F.text.not_in([
#     "Поиск кандидата", "Сохранить тестовое задание", "Найти кандидата", "собственная база", 
#     "через hh", "К созданию вакансии", "Создать вакансию", "К поиску кандидата", "Отмена"
# ]))
# async def process_ai(message: types.Message, state: FSMContext):
#     data_of_candidate = message.text
#     print('data_of_candidate - ', data_of_candidate)
#     await state.set_state(DocumentInfoStates)
#     data = await state.get_data()
#     data_of_resumes = data['waiting_for_data_of_resumes']
#     await search_good_resumes(message, data_of_resumes, data_of_candidate)

# Обработчик отправки файла
@router.message((F.document) & (F.from_user.id == ADMIN))
async def handle_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        await state.set_state(DocumentInfoStates)
        await state.update_data(waiting_for_id_document=file_id)
        await state.update_data(waiting_for_name_document=file_id)
        data = {
            'id_document': file_id,
            'name_document': file_name
        }
        await process_ai(message, state, data)
        
        # keyboard = ReplyKeyboardMarkup(
        #     keyboard=[
        #         [
        #             # types.KeyboardButton(text="Сохранить тестовое задание"),
        #             types.KeyboardButton(text="Поиск кандидата"),
        #         ],
        #         [
        #             types.KeyboardButton(text="Сохранить тестовое задание"),
        #         ]
        #     ],
        #     resize_keyboard=True
        # )
        # await message.answer(f"Получен файл: {file_name}! Что с ним сделать?", reply_markup=keyboard)

# # Обработчик создания вакансии
# @router.message(F.text.in_(["Создать вакансию","К созданию вакансии"]))
# async def create_vacancy(message: types.Message):
#     await message.answer("Для составления вакансии нам понадобится следующая информация:\
# Портрет кандидата; (возраст, мин опыт, пол);\
# Условия вакансии (требования, обязанности);\
# Специальные пожелания по опыту кандидатов;\
# Согласование списка вопросов для интервью с кандидатами.\
# На что приоритетнее отталкиваться при фильтрации резюме, собеседовании и проверке тестового задания?"
#     )

# Переписать текст вакансии
@router.message((F.text.in_(["Переписать"])) & (F.from_user.id == ADMIN))
async def regenerate_text_of_vacancy(message: types.Message, state: FSMContext):
    await message.answer('Хорошо! Давайте перепишем...')
    await state.set_state(ChatHistory) 
    history = await get_history_by_user_id(message.from_user.id, state)
    new_request = history + [{'role': 'user', 'content': 'Мне не понравился результат. Уточни, что добавить или убрать, собери всю необходимую для написания вакансии информацию и сгенерируй новый текст вакансии.'}]
    resp = await process_commitment_global(message, new_request, state)
    # keyboard = ReplyKeyboardMarkup(
    #             keyboard=[
    #                 [
    #                     types.KeyboardButton(text="Разместить на hh.ru"),
    #                 ],
    #                 [
    #                     types.KeyboardButton(text="Переписать"),
    #                 ],
    #             ],
    #             resize_keyboard=True
    #         )
    # await message.answer("Если вас не устраивает текст, нажмите кнопку Переписать", reply_markup=keyboard)
# Обработчик выбора проблемы
@router.message((F.text.not_in([
    "Поиск кандидата", "Найти кандидата", "собственная база", 
    "через hh", "К созданию вакансии", "Создать вакансию", "К поиску кандидата", "Отмена"
])) & (F.from_user.id == ADMIN))
async def process_ai(message: types.Message, state: FSMContext, data=None):
    await state.set_state(ChatHistory) 
    # await message.answer(, reply_markup=types.ReplyKeyboardRemove())
    if data:
        await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': f'ты получил файл с именем {data['name_document']} и id {data['id_document']}. Переспроси у меня, что делать с файлом(пиши только название файла), возможно это файл с тестовым заданием или с резюме кандидатов.'}, state)
        history = await get_history_by_user_id(message.from_user.id, state)
        print(history)
        resp = await process_commitment_global(message, history, state)
    else:
        await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': message.text}, state)
        history = await get_history_by_user_id(message.from_user.id, state)
        resp = await process_commitment_global(message, history, state)
    print(f'!!!! resp: {resp}')
    if resp:
        await message.answer(resp)
    # asyncio.run(process_commitment(message))

        # keyboard = ReplyKeyboardMarkup(
        #     keyboard=[
        #         [
        #             types.KeyboardButton(text="К поиску кандидата"),
        #         ],
        #         [
        #             types.KeyboardButton(text="К созданию вакансии")
        #         ]
        #     ],
        #     resize_keyboard=True
        # )
        # await message.answer("Что делать дальше?", reply_markup=keyboard)

async def send_sms_for_help_create_vacancy(message: types.Message, state: FSMContext):
    await message.answer("К сожалению, данной информации не достаточно. Ответьте на следующие вопросы..")
    await process_hh(message, state)

async def save_vacancy(data):
    # await message.answer("Сохраняю вакансию и портрет кандидата...")
    save_vacancy_info(data)
    save_candidate_info(data)

async def save_test_task(message: types.Message, state: FSMContext, arguments):
    session = get_db()  # Получаем сессию с базой данных
    print(arguments)
    # Проверяем, существует ли вакансия с таким же названием в базе
    title = arguments["title_of_vacancy"]
    existing_vacancy = session.query(Vacancies).filter_by(title=title.capitalize()).first()
    
    if existing_vacancy:
        # Если вакансия уже существует, обновляем ее
        existing_vacancy.test_task = json.dumps(arguments)
       
        session.commit()
        await message.answer(f"Тестовое задание для вакансии '{title}' сохранено в базу.")
    else:
        # Если вакансии с таким названием нет, просто сохраняем новую
        await message.answer(f"Вакансии с названием '{title}' не существует.")


# Поиск кандидата по БД
async def look_for_candidate_by_db(message: types.Message, state: FSMContext, arguments):
    
    data = arguments
    list_structured_resumes = await parser(data.get('id_document'))
    data['data_of_resumes'] = list_structured_resumes
    with open("resumes.txt", "w", encoding='utf-8') as f:
        for k, v in enumerate(json.loads(list_structured_resumes).items()):  # json.loads преобразует json в python-объекты 
            print('i - ', v)
            print(f'{v[0]}: {v[1]}', file=f)
    await search_vacancies(message, state, data)

client = AsyncOpenAI(api_key=GPT_KEY)
async def process_commitment_global(message: types.Message, history, state: FSMContext):
    

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание.  Ты  интегрирован  с  API  HeadHunter,  Bitrix24  и  OpenAI. Ты помнишь всю переписку с пользователем.\
              **Твои  основные  задачи:**\
              *   **Поиск  кандидатов на вакансию:**  Помоги  найти кандидаов на вакансии  через  HeadHunter  или собственную базу резюме.\
              *   **Если ты получаешь мало информации о вакансии(Обязательно должны быть следующие параметры:\
портрет кандидата: Каким должен быть идеальный кандидат?: пол / возраст / хотя бы 2 личных качества / минимальный опыт / навыки\
условия: график / зп / удаленно-офлайн / бонусы есть-нет / kpi есть-нет\
требования: хотя бы 2 качества/навыка\
обязанности: перечислено что будет делать кандидат на работе, хотя бы 2 задачи указано\
вопросы на интервью: минимум 3 вопроса и какой должен быть идеальный ответ\
на что приоритетнее отталкиваться при финальном выборе: указано хотя что-то одно):** 1-2 пункта из списка не придумывай, а напиши подсказку, какую информацию предоставить.\
              *   **Если ты получаешь всю информацию о вакансии:** прописаны все пункты о вакансии в полном объеме, для этого проверяй всю переписку, спроси есть ли что еще добавить или поменять, а затем необходимо вызвать функцию 'save_vacancy()'\
              *   **Если ты получаешь недостаточно информации о вакансии:** до 3 пунктов о вакансии не придумывай, а начни задавать уточняющие вопросы по каждому пункту отдельно, ты будешь помнить каждый ответ от пользователя, так ка у тебя есть память. Пример уточняющего вапроса: Вы не написали желаемяй возраст кандидата. Уточните его, пожалуйста.'\
              *   **Если ты получил докунент с тестовыь заданием:**  собери всю необходимую инфонмацию: название вакансии, название документа, id документа, время выполнения задания в днях, и вызови функцию 'save_test_task()'.\
              *   **Если ты получил докунент с резюме:**  тебе необходимо уточнить нужно ли создавать вакансию, если да то приступаешь к ее созданию, задавая необходимые вопросы.\
              *   **Если ты получил докунент с резюме и создавать вакансию не надо:**  нужно обязательно создать портрет кандидата(на какую должность ищем кандидата / пол / возраст / хотя бы 2 личных качества / минимальный опыт / навыки), по каторому ты будешь выбирать подходящие резюме, уточняешь всю информацию, задавая вопросы, и вызываешь функцию 'look_for_candidate_by_db()').\
              *   **Применение функций:**  Для выполнения поставленных задачь обязательно применяй следующие функции: 'save_vacancy()' - для сохранения вакансии в базе данных, 'save_test_task()' - Сохраняет в базу данных тестовое задание в виде id документа, названия документа, названия вакансии и времени выполнения задания, 'look_for_candidate_by_db()'- ищет кандидатов в базе резюме по портрету(описанию).\
              *   **Отправка  вакансии:**  Помоги  отправить вакансию  на  HeadHunter  или  Bitrix24.\
              *   **Создание  лидов  в  Bitrix24:**  Создавай  новые  лиды  в  Bitrix24  для  кандидатов,  которые  связались  с  ботом.\
              *   **Генерация  тестовых  заданий:**  Используй  OpenAI  для  генерации  тестовых  заданий  для  кандидатов.\
              *   **Администрирование:**  Предоставь  администратору  доступ  к  панели  управления  вакансиями,  кандидатами  и  отчетами.\
                **Дополнительные  инструкции:**\
              *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
              *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывае, если не просят.\
              *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
#     prompt = "You are a smart and friendly HR bot that helps users find vacancies, send a resume, pass an interview and get a test task. You are integrated with the API HeadHunter, Bitrix24 and OpenAI. You remember all the correspondence with the user.\
# **Your main tasks:** \
# * **Search for candidates for a vacancy:** Help find candidates for vacancies through HeadHunter or your own resume database. \
# * **If you receive little information about a vacancy (The following parameters must be present: \
# candidate profile: What should an ideal candidate be like?: gender / age / at least 2 personal qualities / minimum experience / skills \
# conditions: schedule / salary / remote-offline / bonuses yes-no / kpi yes-no \
# requirements: at least 2 qualities/skills \
# responsibilities: what the candidate will do at work is listed, at least 2 tasks are indicated \
# interview questions: minimum 3 questions and what the ideal answer should be\
# What is the most important thing to start with when making the final choice: at least one of them is specified):** Don't make up 1-2 items from the list, but write a hint on what information to provide.\
# * **If you receive all the information about the vacancy:** All the items about the vacancy are written in full, to do this, check all the correspondence, ask if there is anything else to add or change, and then you need to call the 'save_vacancy()' function\
# * **If you do not receive enough information about the vacancy:** Don't make up up to 3 items about the vacancy, but start asking clarifying questions for each item separately, you will remember each answer from the user, since you have a memory. An example of a clarifying question: You did not write the desired age of the candidate. Please specify it.'\
# * **Using functions:** To complete the tasks, be sure to use the following functions: 'save_vacancy()' - to save the vacancy in the database.\
# * **Sending a vacancy:** Help send a vacancy to HeadHunter or Bitrix24.\
# * **Creating leads in Bitrix24:** Create new leads in Bitrix24 for candidates who contacted the bot.\
# * **Generating test tasks:** Use OpenAI to generate test tasks for candidates.\
# * **Administration:** Grant the administrator access to the control panel for vacancies, candidates and reports.\
# **Additional instructions:**\
# * Always write in Russian.\
# * Be polite and friendly when communicating with users.\
# * Provide clear and understandable instructions do not invent anything if you do not ask.\
# * Use text formatting for better visual presentation of information."
              
            #   \
            #   *   Обрабатывай  ошибки  и  предоставляй  пользователям  информативные  сообщения  об  ошибках."  *   **Если ты получаешь недостаточно информации о вакансии:** до 3 пунктов о вакансии и не в полном объеме ничего не придумывай - необходимо вызвать функцию 'send_sms_for_help_create_vacancy()'\
    #  
    tools = [
        # {"type": "function",
        #  "function": {
        #         "name": "send_sms_for_help_create_vacancy",
        #         "description": "Собирает информацию о вакансии при помощи опроса.",
        #     },
        # },
        {"type": "function",
         "function": {
                "name": "save_vacancy",
                "description": "Отправляет информацию о вакансии в базу данных.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title_of_vacancy": {"type": "string"},
                        "conditions": {"type": "string"},
                        "requirements": {"type": "string"},
                        "responsibilities": {"type": "string"},
                        "interview_questions": {"type": "string"},
                        "priority": {"type": "string"},
                        "ideal_candidate": {"type": "string"},
                        "demographics": {"type": "string"},
                        "qualities": {"type": "string"},
                        "skills": {"type": "string"},
                    },
                    "required": ["title_of_vacancy", "conditions", "requirements", "responsibilities", "interview_questions", "priority", "ideal_candidate", "demographics", "qualities", "skills"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "save_test_task",
                "description": "Сохраняет в базу данных тестовое задание в виде id документа, названия документа, названия вакансии и времени выполнения задания.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id_document": {"type": "string"},
                        "name_document": {"type": "string"},
                        "title_of_vacancy": {"type": "string"},
                        "time_to_complete": {"type": "string"},
                    },
                    "required": ["id_document", "name_document", "title_of_vacancy", "time_to_complete"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "look_for_candidate_by_db",
                "description": "Сохраняет в базу данных тестовое задание в виде id документа, названия документа, названия вакансии и времени выполнения задания.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "waiting_for_ideal_candidate": {"type": "string"},
                        "waiting_for_demographics": {"type": "string"},
                        "waiting_for_qualities": {"type": "string"},
                        "waiting_for_skills": {"type": "string"},
                        "id_document": {"type": "string"},
                        "name_document": {"type": "string"},
                    },
                    "required": ["id_document", "name_document", "waiting_for_ideal_candidate", "waiting_for_demographics", "waiting_for_qualities", "waiting_for_skills"],
                },
            },
        },
    ]
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
        ] + history,
        tools=tools
    )

# *3.  Обработка  ответа  ChatGPT:**
    print(response.choices[0].message.content)
    arguments_object = ''
    try:
        tool_call = response.choices[0].message.tool_calls[0]
        arguments_object = tool_call.function.arguments
    except:
        pass
    
    # if response.choices[0].message.content == "function_call":
    if response.choices[0].message.content == None and arguments_object:
        
        arguments = json.loads(arguments_object)
        print('!!!! в функции gpt')
        # function_call = response.choices[0].message.function_call
        function_name = tool_call.function.name
        
        if function_name == "save_test_task":
            await save_test_task(message, state, arguments)
        elif function_name == "look_for_candidate_by_db":
            print('arg for func look_for..', arguments)
            await look_for_candidate_by_db(message, state, arguments)
        elif function_name == "save_vacancy":
            print('!!!! сохраняет вакансию в бд')
            title_of_vacancy = arguments.get("title_of_vacancy", 'уточнить название вакансии')
            conditions = arguments.get("conditions", 'уточнить условия')
            requirements = arguments.get("requirements", 'уточнить требования')
            responsibilities = arguments.get("responsibilities", 'уточнить обязанности')
            interview_questions = arguments.get("interview_questions", 'уточнить вопросы для интервью')
            priority = arguments.get("priority", 'уточнить преоритетные требования к кандидату')
            ideal_candidate = arguments.get("ideal_candidate", 'уточнить каким должен быть идеальный кандидат')
            demographics = arguments.get("demographics", 'уточнить демографические данные')
            qualities = arguments.get("qualities", 'уточнить качества кандидата')
            skills = arguments.get("skills", 'уточнить навыки')
            data = {"waiting_for_title_vacancy": title_of_vacancy,
                    "waiting_for_conditions": conditions,
                    "waiting_for_requirements": requirements,
                    "waiting_for_responsibilities": responsibilities,
                    "waiting_for_interview_questions": interview_questions,
                    "waiting_for_priority": priority,
                    "waiting_for_demographics": demographics,
                    "waiting_for_qualities": qualities,
                    "waiting_for_skills": skills,
                    "waiting_for_ideal_candidate": ideal_candidate,
                }
            print(data, '\n\n')
            
            check_data = any(True for i in data.values() if 'уточнить' in i.lower() or 'не указано' in i.lower())
            print('!!!!!\n!!!!!!\n!!!!!!\n\n', check_data)
            if check_data:
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': json.dumps(data)}, state)
                history = await get_history_by_user_id(message.from_user.id, state)
                await process_commitment_global(message, history, state)
            else:
                await save_vacancy(data)
                vacancy = await process_commitment(message, json.dumps(data))
                await update_vacancy_description(title_of_vacancy, vacancy)
                await message.answer(vacancy)
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': vacancy}, state)
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton(text="Разместить на hh.ru"),
                        ],
                        [
                            types.KeyboardButton(text="Переписать"),
                        ],
                    ],
                    resize_keyboard=True
                )
                await message.answer("Если вас не устраивает текст, нажмите кнопку Переписать", reply_markup=keyboard)
    else:
        # if not message.document:
        result = response.choices[0].message.content
        await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': result}, state)
        # session = get_db()
        # vacancy = session.query(Vacancies).filter_by(title=title_of_vacancy).first()
        # if vacancy:
        #     if vacancy.description is not None and vacancy.description.strip():
        #         print('Поле description заполнено')
        #     else:
        #         await update_vacancy_description(title_of_vacancy, result)
        # else:
        #     print(f"Вакансия с названием '{title_of_vacancy}' не найдена.")
        return result
