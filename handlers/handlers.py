from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
# from aiogram.dispatcher.filters import ContentTypesFilter
# from bot import bot
from .search_candidate import search_c
from GPT import process_commitment
from handlers.utils.candidate import CandidateInfoStates, collect_candidate_portrait_info
from .create_vacancy import VacancyInfoStates, collect_vacancy_info
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup

router = Router()

# class CandidateInfoStates(StatesGroup):
#        waiting_for_ideal_candidate = State()
#        waiting_for_demographics = State()
#        waiting_for_qualities = State()
#        waiting_for_skills = State()

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
    await state.set_state(VacancyInfoStates.waiting_for_title)
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
    
@router.message(VacancyInfoStates.waiting_for_title)
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

# Обработчик отправки файла
# @dp.message_handler(content_types=["document", "photo"])
@router.message(F.document)#content_types=["document", "photo"])
# @dp.message_handler(ContentTypesFilter(content_types=["document"]))
async def handle_file(message: types.Message):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        # await message.reply(f"Получен файл: {file_name}")
        # await bot.send_document(chat_id=message.chat.id, document=file_id, caption="Загруженный файл")
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

# Обработчик выбора проблемы
@router.message(F.text.not_in([
    "Поиск кандидата", "Сохранить тестовое задание", "Найти кандидата", "собственная база", 
    "через hh", "К созданию вакансии", "Создать вакансию", "К поиску кандидата"
]))
async def process_ai(message: types.Message):
    # await message.answer(, reply_markup=types.ReplyKeyboardRemove())
    resp = await process_commitment(message)
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


# Для обработки платных услуг
@router.message(F.text == "Получить решение проблемы от бота зоопсихолог Dog Buddy 300 руб.")
async def process_payment(message: types.Message):
    await message.answer("Чтобы получить индивидуальную инструкцию, оплатите 300 рублей.")
    # Здесь должен быть код для обработки оплаты

@router.message(F.text == "Получить консультацию кинолога 1500 руб.")
async def process_cynologist_payment(message: types.Message):
    await message.answer("Чтобы получить консультацию кинолога, оплатите 1500 рублей.")
    # Здесь должен быть код для обработки оплаты