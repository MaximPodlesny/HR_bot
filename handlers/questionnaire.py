import json
from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup

from config import ADMIN
from handlers.utils.get_vacancy_by_title import get_vacancy
from handlers.utils_for_candidate.gpt_for_interview import process_interview
from handlers.utils.record_history_by_user_id import record_history_by_user_id
from handlers.utils_for_candidate.gpt_for_analise_interview import process_analise_interview
from handlers.utils_for_candidate.gpt_for_second_interview import process_sec_interview
from handlers.utils_for_candidate.update_candidate import update_first_interview_by_candidate_id, update_second_interview_by_candidate_id
from states.form import Form

# openai.api_key = "YOUR_OPENAI_API_KEY"
router = Router()

class FirstInterviewInfoStates(StatesGroup):
       waiting_for_1_question_f = State()
       waiting_for_2_question_f = State()
       waiting_for_3_question_f = State()
       waiting_for_4_question_f = State()
       waiting_for_5_question_f = State()
       waiting_for_6_question_f = State()
       waiting_for_7_question_f = State()
       waiting_for_8_question_f = State()
       waiting_for_9_question_f = State()
       waiting_for_10_question_f = State()
       
class SecondInterviewInfoStates(StatesGroup):
       waiting_for_1_question_s = State()
       waiting_for_2_question_s = State()
       waiting_for_3_question_s = State()

cancel = ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Отмена"),
                # types.KeyboardButton(text="собственная база"),
            ],
        ],
        resize_keyboard=True
    )

@router.message((F.text == "Отмена") & (F.from_user.id != ADMIN))
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

async def poll_first_interview(message, state, questions, vacancy):
    for i, question in enumerate(json.loads(questions), 1):
        data = await state.get_data()
        data[f'waiting_for_{i}_question_f'] = question
        await state.update_data(data)
    questions_for_second_interview = vacancy.interview_questions
    # if questions_for_second_interview:
    # await message.answer("Напишите имя вашей собаки, породу, возраст и пол.")

# Обработчик Пройти собеседование
@router.message((F.text == "Пройти собеседование") & (F.from_user.id != ADMIN))
async def interview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title_of_vacancy = data['chosen_vacancy']
    global vacancy
    vacancy = await get_vacancy(title_of_vacancy)
    await state.clear()
    print(vacancy.description, await state.get_state())
    global questions
    questions = await process_interview(message, vacancy.description, state)
    questions = json.loads(questions)
    # await poll_first_interview(message, state, questions, vacancy)
    
    await message.reply(f"{questions.get('Вопрос 1')}", reply_markup=cancel)
    await state.set_state(FirstInterviewInfoStates.waiting_for_1_question_f)

async def collect_responses_interviews_info(message: types.Message, state: FSMContext):
    print("in collect_responses_interviews_info")
    if await state.get_state() == FirstInterviewInfoStates.waiting_for_1_question_f:
        await state.update_data(waiting_for_1_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_2_question_f)
        await message.reply(f"{questions.get('Вопрос 2')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_2_question_f:
        await state.update_data(waiting_for_2_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_3_question_f)
        await message.reply(f"{questions.get('Вопрос 3')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_3_question_f:
        await state.update_data(waiting_for_3_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_4_question_f)
        await message.reply(f"{questions.get('Вопрос 4')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_4_question_f:
        await state.update_data(waiting_for_4_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_5_question_f)
        await message.reply(f"{questions.get('Вопрос 5')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_5_question_f:
        await state.update_data(waiting_for_5_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_6_question_f)
        await message.reply(f"{questions.get('Вопрос 6')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_6_question_f:
        await state.update_data(waiting_for_6_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_7_question_f)
        await message.reply(f"{questions.get('Вопрос 7')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_7_question_f:
        await state.update_data(waiting_for_7_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_8_question_f)
        await message.reply(f"{questions.get('Вопрос 8')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_8_question_f:
        await state.update_data(waiting_for_8_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_9_question_f)
        await message.reply(f"{questions.get('Вопрос 9')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_9_question_f:
        await state.update_data(waiting_for_9_question_f=message.text)
        await state.set_state(FirstInterviewInfoStates.waiting_for_10_question_f)
        await message.reply(f"{questions.get('Вопрос 10')}", reply_markup=cancel)
    elif await state.get_state() == FirstInterviewInfoStates.waiting_for_10_question_f:
        await state.update_data(waiting_for_10_question_f=message.text)
        # responses_with_questions
        # await update_first_interview_by_candidate_id(message.from_user.id, responses_with_questions)
        questions_for_second_interview = vacancy.interview_questions
        if questions_for_second_interview:
            global questions_of_second_interview
            questions_of_second_interview = await process_sec_interview(message, questions_for_second_interview, state)
            await state.set_state(SecondInterviewInfoStates.waiting_for_1_question_s)
            await message.answer(f"Прекрасно! Осталось совсем немного!")
            await message.reply(f"{questions_of_second_interview.get('Вопрос 1')}", reply_markup=cancel)
    elif await state.get_state() == SecondInterviewInfoStates.waiting_for_1_question_s:
        await state.update_data(waiting_for_1_question_s=message.text)
        await state.set_state(SecondInterviewInfoStates.waiting_for_2_question_s)
        await message.reply(f"{questions_of_second_interview.get('Вопрос 2')}", reply_markup=cancel)
    elif await state.get_state() == SecondInterviewInfoStates.waiting_for_2_question_s:
        await state.update_data(waiting_for_2_question_s=message.text)
        await state.set_state(SecondInterviewInfoStates.waiting_for_3_question_s)
        await message.reply(f"{questions_of_second_interview.get('Вопрос 3')}", reply_markup=cancel)
    elif await state.get_state() == SecondInterviewInfoStates.waiting_for_3_question_s:
        await state.update_data(waiting_for_3_question_s=message.text)
        data = await state.get_data()
        questions_and_responses_of_first_interview = {item[0]: item[1] for item in zip(questions, [data[f'waiting_for_{i+1}_question_f'] for i in range(10)])}
        questions_and_responses_of_second_interview = {item[0]: item[1] for item in zip(list(questions_of_second_interview.values()), [data[f'waiting_for_{i+1}_question_s'] for i in range(3)])}
        await state.clear()
        resp = await process_analise_interview(message, state, json.dumps([questions_and_responses_of_first_interview, questions_and_responses_of_second_interview]))
        if resp.lower() == 'да':
            await update_first_interview_by_candidate_id(message.from_user.id, json.dumps(questions_and_responses_of_first_interview))
            await update_second_interview_by_candidate_id(message.from_user.id, json.dumps(questions_and_responses_of_second_interview))
            if vacancy.test_task:
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton(text="Получить тестовое задание"),
                            # types.KeyboardButton(text="собственная база"),
                        ],
                        [
                            types.KeyboardButton(text="Отмена"),
                            # types.KeyboardButton(text="собственная база"),
                        ],
                ],
                resize_keyboard=True
            )
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': 'Поздравляю вас с успешным прохождением первых двух этапов отбора! Готовы ли вы выполнить тестовое задание, чтобы пройти в финал и выйти на собеседованием с руководителем отдела?'}, state)
                await message.answer(f"Поздравляю вас с успешным прохождением первых двух этапов отбора! Готовы ли вы выполнить тестовое задание, чтобы пройти в финал и выйти на собеседованием с руководителем отдела?", reply_markup=keyboard)
            else:
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton(text="Готов"),
                            # types.KeyboardButton(text="собственная база"),
                        ],
                        [
                            types.KeyboardButton(text="Не готов"),
                            # types.KeyboardButton(text="собственная база"),
                        ],
                ],
                resize_keyboard=True
                )
                await record_history_by_user_id(message.from_user.id, {'role': 'assistant', 'content': 'Поздравляю вас с успешным прохождением первых двух этапов отбора! Готовы ли вы к собеседованию с руководителем отдела?'}, state)
                await message.answer(f"Поздравляю вас с успешным прохождением первых двух этапов отбора! Готовы ли вы к собеседованию с руководителем отдела?", reply_markup=keyboard)
        elif resp.lower() == 'нет':
            await message.answer(f"Отказ")
        else:
            await message.answer(f"GPT вернул ответ отличный от да и нет")


        

