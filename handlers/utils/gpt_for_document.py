import asyncio
import json
from openai import OpenAI, AsyncOpenAI
from config import GPT_KEY
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# from dotenv import load_dotenv

# load_dotenv()

class ResumesInfoStates(StatesGroup):
       waiting_for_list_contact = State()


client = AsyncOpenAI(api_key=GPT_KEY)
async def process_commitment(message: types.Message, resume, portrait):
# async def process_commitment(pr):

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти подходящих кандидатов на вакансию. Ты помнишь всю переписку с пользователем.\
              **Твоя  задача:**\
              *   **Если ты получил докунент с тестовым заданием:**  собери всю необходимую инфонмацию: название вакансии, название документа, id документа, время выполнения задания в днях, и вызови функцию 'save_test_task()'.\
              *   **Если ты получил докунент с резюме:**  тебе необходимо уточнить нужно ли создавать вакансию, если да то приступаешь к ее созданию, или если нужно создать портрет кандидата, по каторому ты будешь выбирать подходящие резюме, уточняешь всю информацию, задавая вопросы, и вызываешь функцию 'look_for_candidate_by_db()').\
              *   **Применение функций:**  Для выполнения поставленных задачь обязательно применяй следующие функции: 'save_test_task()' - Сохраняет в базу данных тестовое задание в виде id документа, названия документа, названия вакансии и времени выполнения задания, 'look_for_candidate_by_db()'- ищет кандидатов в базе резюме по портрету(описанию).\"
    
    tools = [
        {"type": "function",
         "function": {
                "name": "save_test_task",
                "description": "Сохраняет в базу данных тестовое задание в виде id документа, названия документа, названия вакансии и времени выполнения задания.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id_document": {"type": "string"},
                        "name_document": {"type": "string"},
                        "title_of_vacance": {"type": "string"},
                        "time_to_complete": {"type": "string"},
                    },
                    "required": ["id_document", "name_document", "title_of_vacance", "time_to_complete"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "avoid_resume",
                "description": "В аргумент resume_off добавляет пустую строку.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume_off": {"type": "string"},
                    },
                    "required": ["resume_off"],
                },
            },
        },
    ]
    print()
    print(portrait)
    print()
    print(resume)
    response = await client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
        "role": "system",
        "content": prompt,
        },
        {
        "role": "user",
        "content": f'резюме: {resume}. портрет кандидата: {portrait}.',
        }
      ],
      tools=tools
        # max_tokens=3000
      )
    answer = response.choices[0].message.content
# *3.  Обработка  ответа  ChatGPT:**
    print(response.choices[0].message.content)
    arguments_object = ''
    try:
        tool_call = response.choices[0].message.tool_calls[0]
        arguments_object = tool_call.function.arguments
    except:
        pass
    
    # if response.choices[0].message.content == "function_call":
    if response.choices[0].message.content == None and arguments_object:
        
        arguments = json.loads(arguments_object)
        print('!!!! в функции gpt')
        # function_call = response.choices[0].message.function_call
        function_name = tool_call.function.name
        
        if function_name == "avoid_resume":
            print('!!!! резюме не подходит')
            return ''
        elif function_name == "add_resume":
            print('!!!! добавляем резюме')
            resume = arguments.get("resume", 'уточнить портрет')
            return resume
    else:
        await message.answer(response.choices[0].message.content)
    
async def search_good_resumes(message: types.Message, resumes, portrait, state: FSMContext):
    await state.set_state(ResumesInfoStates.waiting_for_list_contact)
    
    for name, resume in enumerate(json.loads(resumes).items()):
        result = await process_commitment(message, f'{resume[0]}: {resume[1]}', portrait)
        if result:
            try:
                data = await state.get_data()
                if "waiting_for_list_contact" not in data or data.get('waiting_for_list_contact') == None:
                    data["waiting_for_list_contact"] = [(resume[1].get('Телефон', ''), resume[1].get('Телеграм', ''))]
                    await state.set_data(data)
                else:
                    data['waiting_for_list_contact'].append((resume[1].get('Телефон', ''), resume[1].get('Телеграм', '')))
                    await state.set_data(data)

                # if data.get('waiting_for_list_contact') == None or not data.get('waiting_for_list_contact'):
                #     print('!!!!\n\n при пустом значении\n')
                #     await state.update_data(waiting_for_list_contact=[])
                #     data = await state.get_data()
                #     print('!!!! data', data['waiting_for_list_contact'])
                # contacts = data.get('waiting_for_list_contact', []).append((resume[1].get('Телефон', ''), resume[1].get('Телеграм', '')))
            except:
                print('ошибка при сохранении контактов')
                await message.answer(f"Ошибка при сохранении контактов. Процесс запустится повторно через 30 секунд.")
                await asyncio.sleep(30)
                await search_good_resumes(message, resumes, portrait, state)
            
            try:
                await message.answer(f"{resume[1].get('Телефон', '')}\n{resume[1].get('Телеграм', '')}")
            except:
                pass
            await message.answer(f"Резюме подходит под портрет: {resume}")
