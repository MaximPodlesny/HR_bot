from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN
from handlers.handlers_for_candidates import aqeaintance, process_ai, process_commitment_global
from handlers.utils_for_candidate.get_candidate_by_id import get_candidate
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils_for_candidate.update_candidate import update_telegram_id_by_candidate_id


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    print('\n\n!!!!\n\n text of start', message.text)
    if message.from_user.id == ADMIN:
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
    else:
        if ' ' in message.text:
            
            data = await state.get_data()
            if "history" not in data:
                data["history"] = {}
            data["history"][message.from_user.id] = data["history"].get(message.from_user.id, [])  # Сохраняем user ID
            telegram_user_id = message.from_user.id
            try:
                candidate_id = message.text.split(' ')[1]
                candidate = update_telegram_id_by_candidate_id(candidate_id, telegram_user_id)
            except:
                await message.answer("Неправильная ссылка")
            
            if not get_candidate(candidate_id).fio:
                await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': 'Уточни мои имя, фамилию и отчество'}, state)
                await process_ai(message, state)
            elif name:=get_candidate(candidate_id).fio:
                await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': f'Поприветствуй меня по имени и расскажи, что можешь для меня сделать. Мое имя: {name}'}, state)
                await process_ai(message, state)
            
            await state.set_data(data)
            buttons = [
                    [
                        types.KeyboardButton(text="Выбрать вакансию"),
                        # types.KeyboardButton(text="Найти кандидата"),
                    ]
            ]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            await message.answer("Привет! я hr-агент компании Catharsis, рад приветствовать Вас. Ознакомьтесь с нашей презентацией.", reply_markup=keyboard)
        else:
            data = await state.get_data()
            if "history" not in data:
                data["history"] = {}
            data["history"][message.from_user.id] = data["history"].get(message.from_user.id, [])  # Сохраняем user ID
            telegram_user_id = message.from_user.id
            # await aqeaintance(message, state)
            await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': 'Уточни мои имя, фамилию и отчество'}, state)
            await process_ai(message, state)
