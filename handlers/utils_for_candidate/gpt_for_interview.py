from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from openai import AsyncOpenAI

from config import GPT_KEY, ADMIN

client = AsyncOpenAI(api_key=GPT_KEY)
async def process_interview(message: types.Message, title_of_vacancy, state: FSMContext):
    

    prompt = 'Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает пройти  собеседование  и  получить  тестовое  задание.\
              **Твои  основные  задачи:**\
              *   **Написать базовые вопросы для собеседования на вакансию:**  ты получаешь текст вакансии и на основе этого текста пишешь 10 базовых вопросов к кандидату в формате json на русском языке.\
              *   **Образец:**{"Вопрос 1": "Каким вы видите свое будущее в этой компании через год?", ...}'
              
            
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
            {
            "role": "user",
            "content": title_of_vacancy,
            },
        ],
        response_format = {'type': "json_object"}
    )

    return response.choices[0].message.content