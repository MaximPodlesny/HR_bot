import asyncio
import datetime
import json
from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
from openai import AsyncOpenAI


import bot
from config import GPT_KEY, ADMIN
from db.create_table import Vacancies
from handlers.questionnaire import FirstInterviewInfoStates, SecondInterviewInfoStates, collect_responses_interviews_info, interview, poll_first_interview
from handlers.states import UserchatInfoStates
from handlers.utils.add_admin import add_admin_id
from handlers.utils.admins import ADMINS
from handlers.utils.chat_history import ChatHistory
from handlers.utils.del_admin import del_admin_id
from handlers.utils.get_history_by_user_id import get_history_by_user_id
from handlers.utils.get_all_vacansies import get_vacancies
from handlers.utils.get_vacancy_by_title import get_vacancy
from handlers.utils.gpt_for_analise_resumes import ResumesInfoStates, search_good_resumes
from handlers.utils_for_candidate.gpt_for_hi import process_hi
from handlers.utils_for_candidate.gpt_for_interview import process_interview
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils.gpt_for_generate_vacancy import process_commitment
from handlers.utils.parser_pdf import parser
from handlers.utils_for_candidate.update_candidate import new_candidate, time_for_test_task_by_candidate_id, update_time_test_task_by_candidate_id
# from aiogram.dispatcher.filters import ContentTypesFilter
# from bot import bot
from .search_candidate import search_c
from handlers.utils.candidate import CandidateInfoStates, collect_candidate_portrait_info, get_db, save_candidate_info, update_vacancy_description
from .create_vacancy import VacancyInfoStates, collect_vacancy_info, save_vacancy_info
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup

router = Router()

# class DocumentInfoStates(StatesGroup):
#        waiting_for_id_document = State()
#        waiting_for_name_document = State()
#        waiting_for_data_of_resumes = State()

# class UserchatInfoStates(StatesGroup):
#        admin_ids = State()
#        name_of_user = State()
#        chosen_vacancy = State()
#        list_vacancies = State()
#        waiting_for_questions = State()

# Обработчик ответа Cancel
@router.message((F.text == "Отмена") & (~F.from_user.id.in_(ADMINS)))
async def process_hh(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                # types.KeyboardButton(text="Найти кандидата"),
                types.KeyboardButton(text="Выбрать вакансию"),
            ],
        ],
        resize_keyboard=True
    )
    await message.answer("Хорошо! Что будем делать дальше?", reply_markup=keyboard)

# установка id для админки
@router.message((F.text == "admin @"))
async def process_add_admin(message: types.Message, state: FSMContext):
    await add_admin_id(message.from_user.id)

@router.message((F.text == "admin @ -"))
async def process_del_admin(message: types.Message, state: FSMContext):
    await del_admin_id(message.from_user.id)

# @router.message(FirstInterviewInfoStates())
# async def process_poll(message: types.Message, state: FSMContext):
#     answer = await collect_responses_interviews_info(message, state)

@router.message(SecondInterviewInfoStates())
async def process_poll(message: types.Message, state: FSMContext):
    answer = await collect_responses_interviews_info(message, state)

@router.message(UserchatInfoStates.name_of_user)
async def process_poll(message: types.Message, state: FSMContext):
    print('\n\n!!\n\n in state name')
    await state.clear()
    # await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': message.text}, state)
    # history = await get_history_by_user_id(message.from_user.id, state)
    answer = await process_ai(message, state)
    


@router.message(UserchatInfoStates.waiting_for_questions)
async def process_poll(message: types.Message, state: FSMContext):
    await state.clear()
    # await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': message.text}, state)
    # history = await get_history_by_user_id(message.from_user.id, state)
    # await message.answer(, reply_markup=types.ReplyKeyboardRemove())
    # resp = await process_commitment_global(message, history, state)
    await process_ai(message, state)




    

# Выбор вакансии
@router.message((F.text == "Выбрать вакансию") & (~F.from_user.id.in_(ADMINS)))
async def choice_vacancy(message: types.Message, state: FSMContext):
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
        ] + [[types.KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
    )
    # Отправляем сообщение с клавиатурой
    await message.reply("Выберите вакансию:", reply_markup=keyboard)
    # Отправляем опрос
    # await message.reply_poll(poll)

# Пройти тестовое задание
@router.message((F.text == "Получить тестовое задание") & (~F.from_user.id.in_(ADMINS)))
async def give_test_task(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data['waiting_for_vacancy_test'].get('url_to_task'):
        test_task = data['waiting_for_vacancy_test']['url_to_task']
        time_to_complete = data['waiting_for_vacancy_test']['time_to_complete']

    current_date = datetime.now()
    await update_time_test_task_by_candidate_id(message.from_user.id, current_date)
    await message.answer(f"Ваше задание здесь:\n{test_task}\nВремя на выполнение {''.join(i for i in time_to_complete if i.isdigit())} дня!")
    await message.answer(f"Как завершите задание, напишитн мне: 'Тестовое задание выполнено'")


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
    await state.clear()
    # answer = await collect_vacancy_info(message, state)
    # Получаем выбранную вакансию
    chosen_vacancy = message.text

    # Запоминаем выбранную вакансию в контексте пользователя
    await state.update_data(chosen_vacancy=chosen_vacancy)
    # Переходим в следующее состояние (например, для обработки дальнейших действий)
    await state.set_state(UserchatInfoStates())
    data = await state.get_data()
    print('\n\n!!!!\n\n', data, await state.get_state())
    await message.answer(f"Вы выбрали вакансию: {chosen_vacancy}.\n\nПройдите электронное собеседование:")
    await interview(message, state)
    # Отправляем сообщение с выбранной вакансией
    # keyboard = ReplyKeyboardMarkup(
    #         keyboard=[
    #             [
    #                 types.KeyboardButton(text="Пройти собеседование"),
    #             ],
    #             [
    #                 types.KeyboardButton(text="Отмена"),
    #             ],
    #         ],
    #         resize_keyboard=True
    #     )
    

    # # await message.answer("Хорошо! Выберите, что будем делать дальше:", reply_markup=keyboard)
    # await message.answer(text=f"Вы выбрали вакансию: {chosen_vacancy}.\n\nПройдите электронное содеседование:", reply_markup=keyboard)

    # Переходим в следующее состояние (например, для обработки дальнейших действий)
    # await state.clear()
    # print('!!!!\n\n', await state.get_state())
    # await state.set_state(ResumesInfoStates.waiting_for_list_contact)

    

# Обработчик создания вакансии
# @router.message((F.text.in_(["Создать вакансию","К созданию вакансии", "через hh"])) & (F.from_user.id != ADMIN))
# async def process_hh(message: types.Message, state: FSMContext):
#     await message.answer("Нам нужна будет следующяя информация:\
#         \
#         Название вакансии.\
#         \
#         Портрет Кандидата:\
#         \
#         *   Пол / Возраст:  Укажите  желаемый  пол  и  возраст  кандидата.\
#         *   Личные  качества:  Опишите  минимум  два  важных  для  вас  личных  качества  кандидата.\
#         *   Минимальный  опыт:  Укажите  минимальный  опыт  работы,  который  требуется  для  этой  вакансии.\
#         \
#         Условия:\
#         \
#         *   График  работы:  Укажите  желаемый  график  работы  (полный  день,  неполный  день,  гибкий  график  и  т.д.).\
#         *   Заработная  плата:  Укажите  желаемую  заработную  плату.\
#         *   Удаленная  работа / Офис:  Укажите,  будет  ли  работа  удаленной  или  в  офисе.\
#         *   Бонусы:  Укажите,  предусмотрены  ли  бонусы  для  этой  позиции.\
#         *   KPI:  Укажите,  будут  ли  использоваться  KPI  для  оценки  работы  кандидата.\
#         \
#         Требования:\
#         \
#         *   Качества / Навыки:  Опишите  минимум  два  важных  для  вас  качества  или  навыка  кандидата.\
#         \
#         Обязанности:\
#         \
#         *   Задачи:  Перечислите  минимум  две  основные  задачи,  которые  будет  выполнять  кандидат  на  этой  работе.\
#         \
#         Вопросы  на  интервью:\
#         \
#         *   Вопросы:  Сформулируйте  минимум  три  вопроса,  которые  вы  будете  задавать  кандидату  на  интервью.\
#         *   Идеальные  ответы:  Опишите  желаемые  ответы  на  эти  вопросы.\
#         \
#         Приоритеты  при  выборе:\
#         \
#         *   Приоритет:  Укажите,  на  что  вы  будете  обращать  внимание  в  первую  очередь  при  финальном  выборе  кандидата."
#     )
#     await message.answer('Хорошо! Давайте соберем информацию о вакансии.')
    
#     keyboard = ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     types.KeyboardButton(text="Есть портрет"),
#                     types.KeyboardButton(text="Нет портрета"),
#                 ],
#                 [
#                     types.KeyboardButton(text="Отмена"),
#                 ],
#             ],
#             resize_keyboard=True
#     )
#     await message.reply('У Вас уже есть портрет кандидата?', reply_markup=keyboard)
    
# @router.message(VacancyInfoStates.waiting_for_title_vacancy)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     answer = await collect_vacancy_info(message, state)

# @router.message(VacancyInfoStates.waiting_for_conditions)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     print("in look_for_vacancy")
#     # await message.answer('Хорошо! Какими должны быть пол, возраст, минимальный опыт?')
#     # await state.set_state(CandidateInfoStates.waiting_for_demographics)
#     answer = await collect_vacancy_info(message, state)

# @router.message(VacancyInfoStates.waiting_for_requirements)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     answer = await collect_vacancy_info(message, state)

# @router.message(VacancyInfoStates.waiting_for_responsibilities)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     answer = await collect_vacancy_info(message, state)

# @router.message(VacancyInfoStates.waiting_for_interview_questions)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     answer = await collect_vacancy_info(message, state)

# @router.message(VacancyInfoStates.waiting_for_priority)
# async def info_for_vacancy(message: types.Message, state: FSMContext):
#     answer = await collect_vacancy_info(message, state)

# # Обработчик ответа "собственная база"
# @router.message(F.text == "собственная база")
# async def process_my_data(message: types.Message):
#     # search_candidate()
#     await message.answer("Загрузите резюме(csv) и тестовое задание(txt)")


# @router.message((F.document) & (F.from_user.id != ADMIN))
# async def handle_file(message: types.Message, state: FSMContext):
#     if message.document:
#         file_id = message.document.file_id
#         file_name = message.document.file_name
#         await state.set_state(DocumentInfoStates)
#         await state.update_data(waiting_for_id_document=file_id)
#         await state.update_data(waiting_for_name_document=file_id)
        
#         keyboard = ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     # types.KeyboardButton(text="Сохранить тестовое задание"),
#                     types.KeyboardButton(text="Поиск кандидата"),
#                 ],
#                 [
#                     types.KeyboardButton(text="Сохранить тестовое задание"),
#                 ]
#             ],
#             resize_keyboard=True
#         )
#         await message.answer(f"Получен файл: {file_name}! Что с ним сделать?", reply_markup=keyboard)

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
# @router.message((F.text.in_(["Переписать"])) & (F.from_user.id != ADMIN))
# async def regenerate_text_of_vacancy(message: types.Message, state: FSMContext):
#     await message.answer('Хорошо! Давайте перепишем...')
#     await state.set_state(ChatHistory) 
#     history = await get_history_by_user_id(message.from_user.id, state)
#     new_request = history + [{'role': 'user', 'content': 'Мне не понравился результат. Собери всю необходимую для написания вакансии информацию и сгенерируй поновой.'}]
#     resp = await process_commitment_global(message, new_request, state)
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


async def aqeaintance_with_company(message: types.Message, state: FSMContext):
    await message.answer("Позвольте я сначала расскажу вам о нашей компании. тут ссылка.")
    await answer_questions(message, state)

async def answer_questions(message: types.Message, state: FSMContext):
    # await state.set_state(UserchatInfoStates.waiting_for_questions)
    await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': "Не против ли вы ответить на ряд вопросов для дальнейшего отбора?"}, state)
    await asyncio.sleep(3)
    await message.answer("Не против ли вы ответить на ряд вопросов для дальнейшего отбора?")

async def aqeaintance(message: types.Message, state: FSMContext):
    # await state.set_state(UserchatInfoStates.name_of_user)
    await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': "Укажите ваше ФИО, чтобы продолжить общение"}, state)
    await message.answer("Укажите ваше ФИО, чтобы продолжить общение")
    

# Обработчик выбора проблемы
@router.message((F.text.not_in([
    "Пройти собеседование",
    "Выбрать вакансию",
    "Отмена"
])) & (~F.from_user.id.in_(ADMINS)))
async def process_ai(message: types.Message, state: FSMContext):
    # await state.set_state(ChatHistory)
    if '/start' not in message.text:
        await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': message.text}, state)
    history = await get_history_by_user_id(message.from_user.id, state)
    # await message.answer(, reply_markup=types.ReplyKeyboardRemove())
    resp = await process_commitment_global(message, history, state)
    print(f'!!!! resp: {resp}')
    if resp:
        await message.answer(resp)
    # asyncio.run(process_commitment(message))

        # keyboard = ReplyKeyboardMarkup(
        #     keyboard=[
        #         [
        #             types.KeyboardButton(text="Выбрать вакансию"),
        #         ],
        #         # [
        #         #     types.KeyboardButton(text="К созданию вакансии")
        #         # ]
        #     ],
        #     resize_keyboard=True
        # )
        # await message.answer("Что делать дальше?", reply_markup=keyboard)



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
    print(f'\n\n!!!\n\nin process_commitment_global condidate side\n\n')
    

#     prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание. Ты помнишь всю переписку.\
# \
# **Твои  основные  задачи:**\
# \
# *   **Знакомишься с кандидатом:** уточняешь полностью фамилию, имя и отчество.\
# *   **Обрабатываешь ввод полного имени:** \
#     *  Если пользователь написал свои фамилию, имя и отчество:\
#         *   Вызываешь функцию `new_candidate()`, которая создает нового кандидата в базе данных и предлагает ознакомиться с компанией. \
#     *  Если данных не хватает, то уточняешь их. \
# *   **Предлагаешь ознакомиться с компанией:** \
#     *   Пример: 'Давайте для начала расскажу вам о нашей компании?'\
#     *   Если пользователь согласен ознакомиться с компанией: \
#         *   Вызываешь функцию `aqeaintance_with_company()`. \
# *   **Предлагаешь ответить на вопросы по вакансии:** \
#     *   Пример: 'Не против ли вы ответить на ряд вопросов для дальнейшего отбора?' \
#     *   Если пользователь готов ответить на вопросы: \
#         *   Вызываешь функцию `choice_vacancy()`. \
# \
# **Для достижения результата:** используй следующие функции:\
# \
# *   `choice_vacancy()`: выдает список имеющихся вакансий для выбора и запускает процесс опроса.\
# *   `aqeaintance_with_company()`: отправляет презентацию.\
# *   `new_candidate()`: создает нового кандидата в базе данных и предлагает ознакомиться с компанией.\
# \
# **Дополнительные  инструкции:**\
# \
# *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
# *   Предоставляй  четкие  и  понятные  инструкции.\
# *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
    prompt = "You're a smart and friendly HR bot that helps users find jobs, send resumes, get interviews, and test jobs. You remember 50 last messages of correspondence.\
              **Your main tasks:**\
              ** Greet the user by name **\
              * **If the user agrees to learn about the company or has written go in the context of agreeing to learn about the company:** If the user agrees to learn about the company(or has written go), call 'aqeaintance_with_company()'\
              * **If the user has written his/her surname, first name and patronymic in full:** check if the surname, first name and patronymic are present, if something is missing, then clarify it, if the data is complete - call the 'new_candidate()' function.\
              **If the user is ready to answer questions:** call the 'interview()'\
              * **If the user asks to select a position for interview:** call 'choice_vacancy()'\
              **If the user has written that he/she has completed a test job:** If there is no link to the completed test job, ask the user to send a link to the completed test job and after receiving the link, call 'check_time_for_complete_test()'\
              * **To achieve the result:** use the following functions: 'choice_vacancy()' - gives a list of available jobs to choose from and starts the survey process, 'aqeaintance_with_company()' - sends the pre-selected job link, 'aqeaintance_with_company()' - sends a link to the completed job link, 'aqeaintance_with_company()' - sends a link to the completed job link.\
                **write only in Russian**"
    
    # prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание. Ты помнишь 50 последних сообщений переписки.\
    #           **Твои  основные  задачи:**\
    #           *   **Приветствуй пользователя по имени**\
    #           *   **Если пользователь согласен узнать о компании или написал поехали в контексте согласия узнать о компании:** если пользователь согласен ознакомиться с компанией(или написал поехали или Поехали), необходимо вызвать функцию 'aqeaintance_with_company()'\
    #           *   **Если пользователь написал свои фамилию, имя и отчество полностью:** проверяешь есть ли фамилия, имя и отчество, если чего-то нет, то уточняешь, если данные в полном объеме - вызвать функцию 'new_candidate()'\
    #           *   **Если пользователь готов ответить на вопросы:** вызвать функцию 'interview()'\
    #           *   **Если пользователь просит выбрать вакансию для интервью:** вызвать функцию 'choice_vacancy()'\
    #           *   **Если пользователь написал, что тестовое задание выполнил:** если нет ссылки на выполненное тестовое залание, попроси отправить ссылку на выполненное тестовое задание и после получения ссылки вызови функцию 'check_time_for_complete_test()'\
    #           *   **Для достижения результата:** используй следу.щие финкции:'choice_vacancy()' - выдает список имеющихся вакансий для выбора и запускает процесс опроса, 'aqeaintance_with_company()' - отправляет презентацию, 'new_candidate()' - создает нового кандидата в базе данных и предлагает ознакомиться с компанией.\
    #             **Дополнительные  инструкции:**\
    #           *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
    #           *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывай, если не просят.\
    #           *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
                #                 *   **Если пользователь написал имя:** проверяешь есть ли фамилия, имя и отчество, если чего-то нет, то уточняешь\                    *   **Предлагать ответить на вопросы по вакансии:** пример: Не против ли вы ответить на ряд вопросов для дальнейшего отбора?\       *   **Предлагать ознакомиться с компанией:** пример: 'Давайте для начала расскажу вам о нашей компании?'\  *   **Если не известно ФИО пользователя:** узнать фамилию, имя и отчество или вызови функцию 'aqeaintance()'\         *   **Если пользователь указал полные ФИО:** уточнить что будет дальше в формате: 'Формат собеседования будет следующий: 1. расскажу вам о компании, 2. попрошу вас ответить на важные вопросы, 3. Отправлю тестовое задание, если оно есть, 4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии, Если все понятно, напиши - поехали'\
 
    tools = [
        {"type": "function",
         "function": {
                "name": "aqeaintance_with_company",
                "description": "Отправляет информацию о компании.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "choice_vacancy",
                "description": "Выбор вакансии из списка и опрос кандидата.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "interview",
                "description": "Производит интервью кандидата.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title_of_vacancy": {"type": "string"}
                    },
                    "required": ["title_of_vacancy"]
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "new_candidate",
                "description": "Создает нового кандидата в базе данных.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sirname_candidate": {"type": "string"},
                        "first_name_candidate": {"type": "string"},
                        "patronymic_candidate": {"type": "string"},
                        "candidate_id": {"type": "string"},
                        "title_of_vacancy": {"type": "string"},
                    },
                    "required": ["sirname_candidate", "first_name_candidate", "patronymic_candidate", "candidate_id"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "check_time_for_complete_test",
                "description": "Проверяет уложился ли кандидат в сроки выполнения задания. Параметр url_to_test_task - url на тестовое задание",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url_to_test_task": {"type": "string"},
                        },
                    "required": ["url_to_test_task"],
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
        
        if function_name == "aqeaintance_with_company":
            print('\n\n!!!\n\nin aqeaintance_with_company')
            await aqeaintance_with_company(message, state)
        elif function_name == "choice_vacancy":
            print('\n\n!!!\n\nin choice_vacancy')
            await choice_vacancy(message, state)
        elif function_name == "interview":
            print('\n\n!!!\n\nin interview')
            try:
                await interview(message, state, title=arguments.get("title_of_vacancy"))
            except ValueError:
                await choice_vacancy(message, state)
        elif function_name == "check_time_for_complete_test":
            print('\n\n!!!\n\nin check_time_for_complete_test')
            current_date = datetime.now()
            time_for_test = await update_time_test_task_by_candidate_id(message.from_user.id, end_time=current_date)
            difference = current_date - time_for_test['start_date']
            all_time = await time_for_test_task_by_candidate_id(message.from_user.id)
            if difference.days > all_time:
                await message.answer('Вы превысили время выполнения тестового задания.')
            else:
                await message.answer('Мы проверим тестовое задание и свяжемся с Вами.')
                await bot.send_message(chat_id=ADMINS[0], text=f'Ссылка на тестовое задание: {arguments.get("url_to_test_task")}')

        elif function_name == "aqeaintance":
            print('\n\n!!!\n\nin aqeaintance')
            await aqeaintance(message, state)
        elif function_name == "new_candidate":
            print('\n\n!!!\n\nin new_candidate')
            fio = f"{arguments.get('first_name_candidate')} {arguments.get('sirname_candidate')} {arguments.get('patronymic_candidate')}"
            print(fio)
            cand_id = ''
            try:
                await state.clear()
                cand_id = int(arguments.get('candidate_id'))
                title_of_vacancy = arguments.get('title_of_vacancy')
                # await state.set_state(UserchatInfoStates.chosen_vacancy)
                await state.update_data(chosen_vacancy=title_of_vacancy)
                # data['chosen_vacancy'] = title_of_vacancy
                # await state.set_data(data)

            except:
                print('id of candidate is not founded')
            try:
                await new_candidate(cand_id, fio, str(message.from_user.id), title_of_vacancy)
            except Exception as e:
                print(e)
            hi = await process_hi(message, history)
            if hi.lower().strip() == 'да' or hi.lower().strip() == 'да.':
                pass
                # await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': fio}, state)
                # await message.answer('Формат собеседования будет следующий:\n1. расскажу вам о компании\n2. попрошу вас ответить на важные вопросы\n3. Отправлю тестовое задание, если оно есть\n4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии\n\nЕсли все понятно, напиши - поехали')
                # await message.answer('Желаете для начала ознакомиться с компанией?')
                # await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': 'Формат собеседования будет следующий: 1. расскажу вам о компании 2. попрошу вас ответить на важные вопросы\n3. Отправлю тестовое задание, если оно есть\n4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии\n\nЕсли все понятно, напиши - поехали'}, state)
            else:
                await message.answer(hi)
                # await message.answer('Желаете для начала ознакомиться с компанией?')
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': hi}, state)
                # await message.answer(hi)
                await message.answer('Формат собеседования будет следующий:\n1. расскажу вам о компании\n2. попрошу вас ответить на важные вопросы\n3. Отправлю тестовое задание, если оно есть\n4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии\n\nЕсли все понятно, напиши - поехали')
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': 'Формат собеседования будет следующий: 1. расскажу вам о компании 2. попрошу вас ответить на важные вопросы\n3. Отправлю тестовое задание, если оно есть\n4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии\n\nЕсли все понятно, напиши - поехали'}, state)

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
