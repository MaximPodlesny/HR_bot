import asyncio
import json
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Text
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from openai import AsyncOpenAI

from config import GPT_KEY

client = AsyncOpenAI(api_key=GPT_KEY)
# async def process_get_professional_roles(title_of_vacancy):
async def get_info_from_vacancy(message: types.Message, description, state: FSMContext):
    #{"id": "from_four_to_six_hours_in_a_day", "name": "Можно работать сменами по 4–6 часов в день"}

    prompt = 'Ты анализируешь описание вакансии.\
            **Твои  основные  задачи:**\
              *   **При получении вакансии:** найти следующие значения - зарплата, занятость, необходимый опыт и выдать в формате json.\
              *   **Образец:**{"employment": {"id": "full", "name": "Полная занятость"}, "salary": {"currency": "KZT", "from": 100, "gross": false, "to": 500}, "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"}}\
              *   **Варианты значений:** Для графика:{"id": "probation","name": "Стажировка"} или {"id": "part", "name": "Частичная занятость"}; для зарплаты: {"currency": "KZT", "from": 100, "gross": false, "to": 500} или {"currency": "KZT", "from": 100", gross": false}; для опыта: {"id": "noExperience", "name": "Нет опыта"}, {"id": "between1And3", "name": "От 1 года до 3 лет"}, {"id": "between3And6", "name": "От 3 до 6 лет"}, {"id": "moreThan6", "name": "Более 6 лет"}'
              
            
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
            {
            "role": "user",
            "content": description,
            },
        ],
        response_format = {'type': "json_object"}
    )

    print(response.choices[0].message.content)
    return (json.loads(response.choices[0].message.content))
