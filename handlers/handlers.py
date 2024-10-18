from aiogram import Router, types
from aiogram import F
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup
# from aiogram.dispatcher.filters import ContentTypesFilter
# from bot import bot
from .search_candidate import search_c
from GPT import process_commitment

router = Router()

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

# Обработчик ответа "через hh"
@router.message(F.text == "через hh")
async def process_hh(message: types.Message):
    search_c()
    await message.answer("через hh")

# Обработчик ответа "собственная база"
@router.message(F.text == "собственная база")
async def process_my_data(message: types.Message):
    # search_candidate()
    await message.answer("Загрузите резюме(csv) и тестовое задание(txt)")

# Обработчик после получения ботом файла
# @router.message(F.text == "Поиск кандидата" | F.text == "К поиску кандидата")
@router.message(F.text.in_(["Поиск кандидата","К поиску кандидата"]))
async def look_for_candidate(message: types.Message):
    search_c()
    await message.answer("Начинаю поиск...")

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

# Обработчик создания вакансии
@router.message(F.text.in_(["Создать вакансию","К созданию вакансии"]))
async def create_vacancy(message: types.Message):
    await message.answer("Для составления вакансии нам понадобится следующая информация:\
Портрет кандидата; (возраст, мин опыт, пол);\
Условия вакансии (требования, обязанности);\
Специальные пожелания по опыту кандидатов;\
Согласование списка вопросов для интервью с кандидатами.\
На что приоритетнее отталкиваться при фильтрации резюме, собеседовании и проверке тестового задания?"
    )

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