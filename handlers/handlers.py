import json
from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
from openai import AsyncOpenAI

from config import GPT_KEY
from db.create_table import Vacancies
from handlers.utils.chat_history import ChatHistory
from handlers.utils.get_history_by_user_id import get_history_by_user_id
from handlers.utils.gpt_for_analise_resumes import search_good_resumes
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils.gpt_for_generate_vacancy import process_commitment
from handlers.utils.parser_pdf import parser
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
@router.message(F.text == "Отмена")
async def process_hh(message: types.Message):
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
@router.message(F.text == "Нет портрета")
async def find_candidate(message: types.Message, state: FSMContext):
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
@router.message(F.text == "Найти кандидата")
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
@router.message(F.text.in_(["Создать вакансию","К созданию вакансии", "через hh"]))
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
@router.message(F.text == "собственная база")
async def process_my_data(message: types.Message):
    # search_candidate()
    await message.answer("Загрузите резюме(csv) и тестовое задание(txt)")

# Обработчик после получения ботом файла
# @router.message(F.text == "Поиск кандидата" | F.text == "К поиску кандидата")
@router.message(F.text.in_(["Поиск кандидата","К поиску кандидата", "Создать портрет"]))
async def info_for_vacancy(message: types.Message, state: FSMContext):
    await state.set_state(DocumentInfoStates)
    data = await state.get_data()
    list_structured_resumes = await parser(data['waiting_for_id_document'])
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
@router.message(F.text == "Искать")
async def info_for_vacancy(message: types.Message, state: FSMContext):
    # data_of_candidate = await state.get_data()
    # print('data_of_candidate - ', data_of_candidate)
    # await state.set_state(DocumentInfoStates)
    data = await state.get_data()
    data_of_candidate = {
        'идеальный кандидат': data['waiting_for_ideal_candidate'],
        'демографические данные': data['waiting_for_demographics'],
        'качества кандидата': data['waiting_for_qualities'],
        'навыка кандидата': data['waiting_for_skills'],
    }
    
    data_of_resumes = data['waiting_for_data_of_resumes']
    await search_good_resumes(message, data_of_resumes, data_of_candidate)

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
@router.message(F.document)
async def handle_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        await state.set_state(DocumentInfoStates)
        await state.update_data(waiting_for_id_document=file_id)
        await state.update_data(waiting_for_name_document=file_id)
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    # types.KeyboardButton(text="Сохранить тестовое задание"),
                    types.KeyboardButton(text="Поиск кандидата"),
                ],
                [
                    types.KeyboardButton(text="Сохранить тестовое задание"),
                ]
            ],
            resize_keyboard=True
        )
        await message.answer(f"Получен файл: {file_name}! Что с ним сделать?", reply_markup=keyboard)

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
@router.message(F.text.in_(["Переписать"]))
async def regenerate_text_of_vacancy(message: types.Message, state: FSMContext):
    await message.answer('Хорошо! Давайте перепишем...')
    await state.set_state(ChatHistory) 
    history = await get_history_by_user_id(message.from_user.id, state)
    new_request = history + [{'role': 'user', 'content': 'Мне не понравился результат. Собери всю необходимую для написания вакансии информацию и сгенерируй поновой.'}]
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
@router.message(F.text.not_in([
    "Поиск кандидата", "Сохранить тестовое задание", "Найти кандидата", "собственная база", 
    "через hh", "К созданию вакансии", "Создать вакансию", "К поиску кандидата", "Отмена"
]))
async def process_ai(message: types.Message, state: FSMContext):
    await state.set_state(ChatHistory) 
    await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': message.text}, state)
    history = await get_history_by_user_id(message.from_user.id, state)
    # await message.answer(, reply_markup=types.ReplyKeyboardRemove())
    resp = await process_commitment_global(message, history, state)
    print(f'!!!! resp: {resp}')
    if resp:
        await message.answer(resp)
    # asyncio.run(process_commitment(message))

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="К поиску кандидата"),
                ],
                [
                    types.KeyboardButton(text="К созданию вакансии")
                ]
            ],
            resize_keyboard=True
        )
        await message.answer("Что делать дальше?", reply_markup=keyboard)

async def send_sms_for_help_create_vacancy(message: types.Message, state: FSMContext):
    await message.answer("К сожалению, данной информации не достаточно. Ответьте на следующие вопросы..")
    await process_hh(message, state)

async def save_vacancy(data):
    # await message.answer("Сохраняю вакансию и портрет кандидата...")
    save_vacancy_info(data)
    save_candidate_info(data)
    # await message.answer("Вакансия и портрет кандидата сохранены.")

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
на что приоритетнее отталкиваться при финальном выборе: указано хотя что-то одно ):** 1-2 пункта из списка не придумывай, а напиши подсказку, какую информацию предоставить.\
              *   **Если ты получаешь всю информацию о вакансии:** прописаны все пункты о вакансии в полном объеме, для этого проверяй всю переписку, - необходимо вызвать функцию 'save_vacancy()'\
              *   **Если ты получаешь недостаточно информации о вакансии:** до 3 пунктов о вакансии не придумывай, а начни задавать уточняющие вопросы по каждому пункту отдельно, ты будешь помнить каждый ответ от пользователя, так ка у тебя есть память. Пример уточняющего вапроса: Вы не написали желаемяй возраст кандидата. Уточните его, пожалуйста.'\
              *   **Применение функций:**  Для выполнения поставленных задачь обязательно применяй следующие функции: 'save_vacancy()' - для сохранения вакансии в базе данных.\
              *   **Отправка  вакансии:**  Помоги  отправить вакансию  на  HeadHunter  или  Bitrix24.\
              *   **Создание  лидов  в  Bitrix24:**  Создавай  новые  лиды  в  Bitrix24  для  кандидатов,  которые  связались  с  ботом.\
              *   **Генерация  тестовых  заданий:**  Используй  OpenAI  для  генерации  тестовых  заданий  для  кандидатов.\
              *   **Администрирование:**  Предоставь  администратору  доступ  к  панели  управления  вакансиями,  кандидатами  и  отчетами.\
                **Дополнительные  инструкции:**\
              *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
              *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывае, если не просят.\
              *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
              
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
    ]
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
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
        
        if function_name == "send_sms_for_help_create_vacancy":
            await send_sms_for_help_create_vacancy(message, state)
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
