from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext



from handlers.handlers_for_candidates import aqeaintance, process_ai, process_commitment_global
from handlers.states import UserchatInfoStates
from handlers.utils.admins import ADMINS
from handlers.utils.get_admin_ids import get_admins
from handlers.utils_for_candidate.get_candidate_by_id import get_candidate
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils_for_candidate.update_candidate import update_telegram_id_by_candidate_id
from aiogram.fsm.state import State, StatesGroup


router = Router()
# class UserchatInfoStates(StatesGroup):
#        admin_ids = State()
#        chosen_vacancy = State()

# class UserchatInfoStates(StatesGroup):
#        admin_ids = State()
#        name_of_user = State()
#        chosen_vacancy = State()
#        list_vacancies = State()
#        waiting_for_questions = State()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext):
    await state.set_state(UserchatInfoStates())
    data = await state.get_data()
    data['admin_ids'] = get_admins()
    await state.set_data(data)
    ADMINS = data.get('admin_ids')
    print('\n\n!!!\n\n', ADMINS)

    print('\n\n!!!!\n\n text of start', message.text)
    if message.from_user.id in ADMINS:
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
            telegram_user_id = str(message.from_user.id)
            try:
                candidate_id = message.text.split(' ')[1]
                candidate = await get_candidate(candidate_id)
                title_of_vacancy = candidate.title_of_vacancy
                print(candidate_id, title_of_vacancy)
                candidate = await update_telegram_id_by_candidate_id(candidate_id, telegram_user_id)
            except:
                await message.answer("Неправильная ссылка")
            
            cand = await get_candidate(candidate_id)
            if not cand.fio:
                print(' в if not cand.fio:')
                await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': f'Название позиции {title_of_vacancy}. id кандидата {candidate_id}'}, state)
                await process_ai(message, state)
            elif name:=cand.fio:
                print(' в if cand.fio:', name)
                await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': f'Имя: {name}. Название позиции {title_of_vacancy}. id кандидата {candidate_id}'}, state)
                await process_ai(message, state)
            
            await state.set_data(data)
            # buttons = [
            #         [
            #             types.KeyboardButton(text="Выбрать вакансию"),
            #             # types.KeyboardButton(text="Найти кандидата"),
            #         ]
            # ]
            # keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            # await message.answer("Привет! я hr-агент компании Catharsis, рад приветствовать Вас. Ознакомьтесь с нашей презентацией.", reply_markup=keyboard)
        else:
            print('in start')
            data = await state.get_data()
            if "history" not in data:
                data["history"] = {}
            data["history"][message.from_user.id] = data["history"].get(message.from_user.id, [])  # Сохраняем user ID
            telegram_user_id = message.from_user.id
            # await aqeaintance(message, state)
            await record_history_by_user_id(message.from_user.id, {'role': 'user', 'content': 'Уточни мои имя, фамилию и отчество'}, state)
            await process_ai(message, state)
