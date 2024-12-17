import asyncio
import json
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from openai import AsyncOpenAI

from config import GPT_KEY
from .hh import get_professional_roles

client = AsyncOpenAI(api_key=GPT_KEY)
# async def process_get_professional_roles(title_of_vacancy):
async def process_get_professional_roles(message: types.Message, title_of_vacancy, state: FSMContext):
    

    prompt = f"У тебя есть список профессиональных ролей: {get_professional_roles()}"+".\
            **Твои  основные  задачи:**\
              *   **При получении названия вакансии:** выбрать одну наиболее подходящую роль и выдать в формате json.\
              *   **Образец:**{'id': '4', 'name': 'Автомойщик'}"
              
            
    response = await client.chat.completions.create(
        model="gpt-4o",
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

    print(response.choices[0].message.content)
    return (json.loads(response.choices[0].message.content))['id']

if __name__ == '__main__':
    asyncio.run(process_get_professional_roles('Повар'))