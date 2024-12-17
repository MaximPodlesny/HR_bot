from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from openai import AsyncOpenAI

from config import GPT_KEY, ADMIN

client = AsyncOpenAI(api_key=GPT_KEY)
async def process_sec_interview(message: types.Message, questions, state: FSMContext):
    

    prompt = 'Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает пройти  собеседование  и  получить  тестовое  задание.\
              **Твои  основные  задачи:**\
              *   **Переписать вопрсы в json формате:**  ты получаешь текст с вопросами перепиши их в формате json на русском языке.\
              *   **Образец:**{"Вопрос 1": "Каким вы видите свое будущее в этой компании через год?", ...}'
              
            
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
            {
            "role": "user",
            "content": questions,
            },
        ],
        response_format = {'type': "json_object"}
    )

    return response.choices[0].message.content