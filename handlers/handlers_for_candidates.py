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
from handlers.utils.get_all_vacansies import get_vacancies
from handlers.utils.get_vacancy_by_title import get_vacancy
from handlers.utils.gpt_for_analise_resumes import ResumesInfoStates, search_good_resumes
from handlers.utils.gpt_for_interview import process_interview
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

class UserchatInfoStates(StatesGroup):
       chosen_vacancy = State()
       list_vacancies = State()



# Обработчик ответа Cancel
@router.message((F.text == "Отмена") & (F.from_user.id != ADMIN))
async def process_hh(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                # types.KeyboardButton(text="Найти кандидата"),
                types.KeyboardButton(text="Выбрать вакансию"),
            ],
        ],
        resize_keyboard=True
    )
    await message.answer("Хорошо! Выберите, что будем делать дальше:", reply_markup=keyboard)

# Обработчик Пройти собеседование
@router.message((F.text == "Пройти собеседование") & (F.from_user.id != ADMIN))
async def find_candidate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title_of_vacancy = data['chosen_vacancy']
    vacancy = await get_vacancy(title_of_vacancy)
    await state.clear()
    print(vacancy.description, await state.get_state())
    questions = await process_interview(message, vacancy.description, state)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Отмена"),
                # types.KeyboardButton(text="собственная база"),
            ],
        ],
        resize_keyboard=True
    )
    await message.answer(f"Хорошо!\n{questions}", reply_markup=keyboard)
    

# Выбор вакансии
@router.message((F.text == "Выбрать вакансию") & (F.from_user.id != ADMIN))
async def find_candidate(message: types.Message, state: FSMContext):
    all_vacancies = await get_vacancies()
    # Формируем опрос
    options = [vacancy.title for vacancy in all_vacancies]
    await state.set_state(UserchatInfoStates.chosen_vacancy)
    await state.update_data(list_vacancies=options)
    # options = [types.PollOption(vacancy) for vacancy in all_vacancies]
    # poll = await message.answer_poll(
    #     question="Выберите вакансию:",
    #     options=options,
    #     type='regular',
    #     is_anonymous=False,
    #     allows_multiple_answers=False,
        # type='quiz',
    # )
      # Формируем клавиатуру с кнопками
    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for vacancy in all_vacancies:
    #     keyboard.add(vacancy.title)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=vacancy.title)]  # Создаем список кнопок
            for vacancy in all_vacancies
        ],
        resize_keyboard=True,
    )
    # Отправляем сообщение с клавиатурой
    await message.reply("Выберите вакансию:", reply_markup=keyboard)
    # Отправляем опрос
    # await message.reply_poll(poll)

# Обработчик ответа на опрос
# @router.poll_answer()
# async def handle_poll_answer(poll_answer: types.PollAnswer, state: FSMContext):
#     # Получаем выбранную вакансию
#     # chosen_vacancy = poll_answer.options[0].text
#     answer_id = poll_answer.option_ids[0]
#     try:
#         print('!!!! - ', answer_id.text)
#     except:
#         pass
#     data = await state.get_data()
#     chosen_vacancy = data['list_vacancies'][answer_id]
#     # Запоминаем выбранную вакансию (например, в контексте пользователя)
#     await state.update_data(chosen_vacancy=chosen_vacancy)

#     # Отправляем сообщение с выбранной вакансией
#     # await poll_answer.bot.send_message(poll_answer.user.id, f"Вы выбрали вакансию: {chosen_vacancy}")
#     keyboard = ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     types.KeyboardButton(text="Пройти собеседование"),
#                 ],
#                 [
#                     types.KeyboardButton(text="Отмена"),
#                 ],
#             ],
#             resize_keyboard=True
#         )
#     # await message.answer("Хорошо! Выберите, что будем делать дальше:", reply_markup=keyboard)
#     await poll_answer.bot.send_message(poll_answer.user.id, text=f"Вы выбрали вакансию: {chosen_vacancy}.\n\nПройдите электронное содеседование:", reply_markup=keyboard)

# Обработчик выбора вакансии
# @router.message(F.from_user.id != ADMIN)
@router.message(UserchatInfoStates.chosen_vacancy)
async def answer_poll(message: types.Message, state: FSMContext):
    # answer = await collect_vacancy_info(message, state)
    # Получаем выбранную вакансию
    chosen_vacancy = message.text

    # Запоминаем выбранную вакансию в контексте пользователя
    await state.update_data(chosen_vacancy=chosen_vacancy)
    # Переходим в следующее состояние (например, для обработки дальнейших действий)
    await state.set_state(UserchatInfoStates)
    # Отправляем сообщение с выбранной вакансией
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Пройти собеседование"),
                ],
                [
                    types.KeyboardButton(text="Отмена"),
                ],
            ],
            resize_keyboard=True
        )
    

    # await message.answer("Хорошо! Выберите, что будем делать дальше:", reply_markup=keyboard)
    await message.answer(text=f"Вы выбрали вакансию: {chosen_vacancy}.\n\nПройдите электронное содеседование:", reply_markup=keyboard)

    # Переходим в следующее состояние (например, для обработки дальнейших действий)
    # await state.clear()
    print('!!!!\n\n', await state.get_state())
    await state.set_state(ResumesInfoStates.waiting_for_list_contact)

    

# Обработчик создания вакансии
@router.message((F.text.in_(["Создать вакансию","К созданию вакансии", "через hh"])) & (F.from_user.id != ADMIN))
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


@router.message((F.document) & (F.from_user.id != ADMIN))
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
@router.message((F.text.in_(["Переписать"])) & (F.from_user.id != ADMIN))
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
@router.message((F.text.not_in([
    "Поиск кандидата", "Сохранить тестовое задание", "Найти кандидата", "собственная база", 
    "через hh", "К созданию вакансии", "Создать вакансию", "К поиску кандидата", "Отмена"
])) & (F.from_user.id != ADMIN))
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
                    types.KeyboardButton(text="Выбрать вакансию"),
                ],
                # [
                #     types.KeyboardButton(text="К созданию вакансии")
                # ]
            ],
            resize_keyboard=True
        )
        await message.answer("Что делать дальше?", reply_markup=keyboard)

# async def send_sms_for_help_create_vacancy(message: types.Message, state: FSMContext):
#     await message.answer("К сожалению, данной информации не достаточно. Ответьте на следующие вопросы..")
#     await process_hh(message, state)

# async def save_vacancy(data):
#     # await message.answer("Сохраняю вакансию и портрет кандидата...")
#     save_vacancy_info(data)
#     save_candidate_info(data)
#     # await message.answer("Вакансия и портрет кандидата сохранены.")

client = AsyncOpenAI(api_key=GPT_KEY)
async def process_commitment_global(message: types.Message, history, state: FSMContext):
    

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание.\
              **Твои  основные  задачи:**\
              *   **Рассказывать о компании Catharsis**\
                **Дополнительные  инструкции:**\
              *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
              *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывае, если не просят.\
              *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
              
 
    tools = [
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
        pass
        # arguments = json.loads(arguments_object)
        # print('!!!! в функции gpt')
        # # function_call = response.choices[0].message.function_call
        # function_name = tool_call.function.name
        
        # if function_name == "send_sms_for_help_create_vacancy":
        #     await send_sms_for_help_create_vacancy(message, state)
        # elif function_name == "save_vacancy":
        #     print('!!!! сохраняет вакансию в бд')
        #     title_of_vacancy = arguments.get("title_of_vacancy", 'уточнить название вакансии')
        #     conditions = arguments.get("conditions", 'уточнить условия')
        #     requirements = arguments.get("requirements", 'уточнить требования')
        #     responsibilities = arguments.get("responsibilities", 'уточнить обязанности')
        #     interview_questions = arguments.get("interview_questions", 'уточнить вопросы для интервью')
        #     priority = arguments.get("priority", 'уточнить преоритетные требования к кандидату')
        #     ideal_candidate = arguments.get("ideal_candidate", 'уточнить каким должен быть идеальный кандидат')
        #     demographics = arguments.get("demographics", 'уточнить демографические данные')
        #     qualities = arguments.get("qualities", 'уточнить качества кандидата')
        #     skills = arguments.get("skills", 'уточнить навыки')
        #     data = {"waiting_for_title_vacancy": title_of_vacancy,
        #             "waiting_for_conditions": conditions,
        #             "waiting_for_requirements": requirements,
        #             "waiting_for_responsibilities": responsibilities,
        #             "waiting_for_interview_questions": interview_questions,
        #             "waiting_for_priority": priority,
        #             "waiting_for_demographics": demographics,
        #             "waiting_for_qualities": qualities,
        #             "waiting_for_skills": skills,
        #             "waiting_for_ideal_candidate": ideal_candidate,
        #         }
        #     print(data, '\n\n')
            
        #     check_data = any(True for i in data.values() if 'уточнить' in i.lower() or 'не указано' in i.lower())
        #     print('!!!!!\n!!!!!!\n!!!!!!\n\n', check_data)
        #     if check_data:
        #         await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': json.dumps(data)}, state)
        #         history = await get_history_by_user_id(message.from_user.id, state)
        #         await process_commitment_global(message, history, state)
        #     else:
        #         await save_vacancy(data)
        #         vacancy = await process_commitment(message, json.dumps(data))
        #         await update_vacancy_description(title_of_vacancy, vacancy)
        #         await message.answer(vacancy)
        #         await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': vacancy}, state)
        #         keyboard = ReplyKeyboardMarkup(
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
        #         await message.answer("Если вас не устраивает текст, нажмите кнопку Переписать", reply_markup=keyboard)
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
