from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    
    data = await state.get_data()
    if "history" not in data:
        data["history"] = {}
    data["history"][message.from_user.id] = data["history"].get(message.from_user.id, [])  # Сохраняем user ID
    
    await state.set_data(data)
    buttons = [
            [
                types.KeyboardButton(text="Создать вакансию"),
                types.KeyboardButton(text="Найти кандидата"),
            ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Привет! я hr-агент компании Catharsis, моя задача автоматизировать поиск и отбор кандидатов для ваших вакансий. Чем могу помочь?", reply_markup=keyboard)
