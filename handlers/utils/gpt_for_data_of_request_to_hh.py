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
async def get_req_to_gpt_for_hh(description):
    #{"id": "from_four_to_six_hours_in_a_day", "name": "Можно работать сменами по 4–6 часов в день"}

    prompt = 'Ты формируешь data в json формате для запроса к api hh.ru для получения резюме по описанию кандидата.\
            Для этого используй эти пояснения: /resumes?text=программист – найдет все резюме, в любом месте которого встречается заданное слово "программист",\
            /resumes?text=программист&text=java – найдет резюме, в любом месте которого встречаются слова "программист" и "java",\
            /resumes?text=программист%20java&text.logic=any&text.field=everywhere&text.period=all_time – найдет резюме, в любом месте которого встречается любое из слов заданной фразы в параметре text ("программист" или "java"). При использовании дополнительных полей, они должны быть указаны все,\
            /resumes?text=Headhunter&text.logic=all&text.field=experience&text.period=last_three_years – найдет все резюме, в опыте работы которых за последние 3 года встречается "Headhunter",\
            /resumes?text=менеджер%20проекта&text.logic=all&text.field=experience%2Cskills&text.period=last_year&text=ответственный&text.logic=all&text.field=everywhere&text.period=all_time – найдет все резюме, в опыте работы за последний год и ключевых навыках которых встречаются слова "менеджер" и "проекта", а также слово "ответственный" в любом месте резюме. Отметим, что дополнительные параметры text.logic=all&text.field=experience%2Cskills&text.period=last_year указаны для text=менеджер%20проекта, а text.logic=all&text.field=everywhere&text.period=all_time для параметра text=ответственный.\
            *Поясрения:* text - Поисковая фраза. Метод найдет резюме, в которых встречаются все слова заданной фразы.\
                        Особенности:\
                        Можно указать несколько значений. Каждое дополнительное значение уточняет поиск.\
                        В качестве поисковой фразы можно использовать язык поисковых запросов.\
                        Специально для этого поля предусмотрено автодополнение по подсказкам.\
                        Для тонкой настройки по фразе можно использовать параметры text.logic, text.field, text.period. При использовании дополнительных text.* полей, необходимо указывать весь набор (триаду) параметров\
                        text.field - Описывает, где должны встречаться слова из поисковой фразы text. Можно указать несколько значений через запятую, например ?text.field=education,keywords.\
                        text.logic - Описывает, как производится поиск.\
            **Основные значения:** для text.field - [{"id": "everywhere", "name": "везде"}, {"id": "title", "name": "в названии резюме"}, {"id": "education", "name": "в образовании"}, {"id": "skills", "name": "в ключевых навыках"}, {"id": "experience", "name": "в опыте работы"}, {"id": "experience_company", "name": "в компаниях и отраслях"}, {"id": "experience_position", "name": "в должностях"}, {"id": "experience_description", "name": "в обязанностях"}],\
                                    для text.logic - [{"id": "all", "name": "Все слова встречаются"}, {"id": "any", "name": "Любое из слов встречается"}, {"id": "phrase", "name": "Точная фраза встречается"}, {"id": "except", "name": "Не встречаются"}],\
                                    для experience -  [{"id": "noExperience","name": "Нет опыта"},{"id": "between1And3","name": "От 1 года до 3 лет"},{"id": "between3And6","name": "От 3 до 6 лет"},{"id": "moreThan6","name": "Более 6 лет"}],\
                                    для gender - [{"id": "male","name": "Мужской"},{"id": "female","name": "Женский"}],\
            *Образец data:* {"text": "программист", "text.logic": "any", "text.field": "experience", "text.period": "", "age_from": "20", "age_to": "45", "experience": {"id": "noExperience","name": "Нет опыта"}, "gender": {"id": "male","name": "Мужской"}, "page": 0}\
            *Поле "page" в data добавлять всегда со значением 0*\
            *Поле "text.period" в data добавлять всегда со значением ""*\
            *Если каких-то данных в описании нет, то их в data не добавлять*'
              
            
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
            {
            "role": "user",
            "content": f'Описание кандидата: {description}',
            },
        ],
        response_format = {'type': "json_object"}
    )

    print(f'!!!\n\n data for hh \n\n {response.choices[0].message.content}')
    return (json.loads(response.choices[0].message.content))
