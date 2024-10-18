from aiogram import Router, types
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import Message

from states.form import Form

# openai.api_key = "YOUR_OPENAI_API_KEY"
router = Router()

@router.message(F.Text == "Получить решение проблемы от бота зоопсихолог Dog Buddy 300 руб.")
async def start_questions(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Напишите имя вашей собаки, породу, возраст и пол.")

@router.message(StateFilter(Form.name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.behavior)
    await message.answer("Опишите конкретное негативное поведение на улице, которое ваша собака проявляет в данный момент.")

@router.message(StateFilter(Form.behavior))
async def process_behavior(message: Message, state: FSMContext):
    await state.update_data(behavior=message.text)
    await state.set_state(Form.reason)
    await message.answer("Что по вашему мнению провоцирует такое поведение?")

@router.message(StateFilter(Form.reason))
async def process_reason(message: Message, state: FSMContext):
    await state.update_data(reason=message.text)
    await state.set_state(Form.frequency)
    await message.answer("Как часто собака ведет себя подобным образом? (постоянно, раз в день, в несколько дней и т.д.)")

@router.message(StateFilter(Form.frequency))
async def process_frequency(message: Message, state: FSMContext):
    await state.update_data(frequency=message.text)
    await state.set_state(Form.reaction)
    await message.answer("Как вы в настоящее время реагируете на поведение собаки?")

@router.message(StateFilter(Form.reaction))
async def process_reaction(message: Message, state: FSMContext):
    await state.update_data(reaction=message.text)
    await state.set_state(Form.measures)
    await message.answer("Какие меры уже предприняли, чтобы попытаться решить эту проблему?")

@router.message(StateFilter(Form.measures))
async def process_measures(message: Message, state: FSMContext):
    await state.update_data(measures=message.text)
    await state.set_state(Form.goal)
    await message.answer("Ближайшая цель: как бы вы хотели, чтобы собака себя вела в идеале?")

@router.message(StateFilter(Form.goal))
async def process_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(Form.commitment)
    await message.answer("Готовы ли вы заниматься с собакой минимум 1 раз в день, чтобы изменить поведение?")

@router.message(StateFilter(Form.commitment))
async def process_commitment(message: Message, state: FSMContext):
    await state.update_data(commitment=message.text)
    
    data = await state.get_data()
    prompt = f"Веди себя, как зоопсихолог, который практикует гуманные способы работы с собакой. Я пришлю тебе описание ситуации с собакой, которая беспокоит меня сейчас, а также другую важную информацию. Ты проанализируешь информацию и дашь мне точную инструкцию в виде последовательности действий, что нужно сделать, чтобы прекратить описанное поведение собаки. Вот информация: {data}"
    
    # Используем OpenAI для получения инструкции (замените это на ваш метод)
    # response = openai.Completion.create(
    #   model="text-davinci-003",
    #   prompt=prompt,
    #   max_tokens=1500
    # )

    await message.answer("Я подготовил для вас индивидуальную инструкцию под ваш запрос. Хочешь получить рекомендацию?")
    await state.clear()
