from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import hh_api, openai_utils, db_utils, message_utils
from db.models import Candidate

class CandidateStates(StatesGroup):
    searching_hh = State()
    collecting_info = State()
    processing_resume = State()
    interviewing = State()
    test_task = State()

async def search_candidates_on_hh(message: types.Message, state: FSMContext):
    """Searches for candidates on HH.ru."""
    vacancy_id = message.text.split()[1]  # Assuming command is like /search_hh <vacancy_id>
    vacancy = await db_utils.get_vacancy(vacancy_id)
    if vacancy:
        candidates = await hh_api.search_candidates(vacancy.title)
        if candidates:
            await message.reply(message_utils.format_hh_search_results(candidates))
            await state.set_state(CandidateStates.collecting_info.state)
            await state.update_data(vacancy_id=vacancy_id, candidates=candidates)
        else:
            await message.reply("Кандидаты по этой вакансии не найдены на HH.ru")
    else:
        await message.reply("Вакансия не найдена")

async def collect_candidate_info(message: types.Message, state: FSMContext):
    """Collects candidate information from the user."""
    async with state.proxy() as data:
        vacancy_id = data.get("vacancy_id")
        candidates = data.get("candidates")
        candidate_index = int(message.text) - 1 # Adjust index to 0-based
        if 0 <= candidate_index < len(candidates):
            candidate_data = candidates[candidate_index]
            # Update candidate_data with additional information from user input
            candidate = Candidate(vacancy_id=vacancy_id, **candidate_data)
            await db_utils.save_candidate(candidate)
            await message.reply("Кандидат добавлен!")
            await state.set_state(CandidateStates.processing_resume.state)
            await state.update_data(candidate_id=candidate.id)
        else:
            await message.reply("Неверный выбор кандидата. Пожалуйста, введите число из списка.")

async def process_candidate_resume(message: types.Message, state: FSMContext):
    """Processes uploaded candidate resume."""
    async with state.proxy() as data:
        candidate_id = data.get("candidate_id")
    # Implement logic to process uploaded resume (file or text)
    # Extract relevant information from the resume
    # Update the Candidate record in the database
    await message.reply("Резюме обработано!")
    await state.set_state(CandidateStates.interviewing.state)

async def interview_candidate(message: types.Message, state: FSMContext):
    """Conducts an interview with the candidate."""
    async with state.proxy() as data:
        candidate_id = data.get("candidate_id")
        vacancy_id = data.get("vacancy_id")
    vacancy = await db_utils.get_vacancy(vacancy_id)
    if vacancy:
        # Use OpenAI to generate interview questions based on the vacancy
        questions = openai_utils.generate_interview_questions(vacancy.description, vacancy.requirements)
        for question in questions:
            await message.reply(question)
            # Wait for the candidate's answer and store it in the database
            # Analyze the candidate's response using OpenAI
            # Provide feedback to the user
    else:
        await message.reply("Вакансия не найдена.")

async def assign_test_task(message: types.Message, state: FSMContext):
    """Assigns a test task to the candidate."""
    # Implement logic to generate or retrieve a test task based on the vacancy
    # Send the test task to the candidate
    await message.reply("Тестовое задание отправлено. Ожидаем ваш ответ.")
    await state.set_state(CandidateStates.test_task.state)

async def process_test_task(message: types.Message, state: FSMContext):
    """Processes the submitted test task."""
    # Implement logic to evaluate the submitted test task 
    # Update the Candidate record with the result
    await message.reply("Тестовое задание принято. Ожидаем вашего ответа.")
    await state.finish()

def setup(dp):
    dp.register_message_handler(search_candidates_on_hh, commands=["search_hh"])
    dp.register_message_handler(collect_candidate_info, state=CandidateStates.collecting_info)
    dp.register_message_handler(process_candidate_resume, state=CandidateStates.processing_resume)
    dp.register_message_handler(interview_candidate, state=CandidateStates.interviewing)
    dp.register_message_handler(assign_test_task, commands=["test_task"])
    dp.register_message_handler(process_test_task, state=CandidateStates.test_task)