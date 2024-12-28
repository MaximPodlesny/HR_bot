import asyncio
import json
from openai import OpenAI, AsyncOpenAI
from config import GPT_KEY
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from handlers.utils.candidate import create_candidate, get_id_candidate_by_fio
# from dotenv import load_dotenv

# load_dotenv()

class ResumesInfoStates(StatesGroup):
       waiting_for_list_contact = State()


client = AsyncOpenAI(api_key=GPT_KEY)
async def process_commitment_for_hh(resume, vacancy):
# async def process_commitment(pr):

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  найти подходящих кандидатов на вакансию.\
              **Твоя  задача:**\
              *   **Проанализировать резюме:** ты получаешь информацию из резюме кандидата и описание вакансии, далее проверяешь подходит ли кандидат для данной вакансии.\
              *   **Если резюме подходит:** вызвать функцию 'add_resume()'\
              *   **Если резюме не подходит:** вызвать функцию 'avoid_resume()'"
    
    tools = [
        {"type": "function",
         "function": {
                "name": "add_resume",
                "description": "Добавляет резюме в список.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resume": {"type": "string"},
                    },
                    "required": ["resume"],
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
   
    response = await client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
        "role": "system",
        "content": prompt,
        },
        {
        "role": "user",
        "content": f'информация из резюме: {resume}. описание вакансии: {vacancy}.',
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
            return 1
    # else:
    #     await message.answer(response.choices[0].message.content)
    
# async def search_good_resumes(message: types.Message, resumes, portrait, state: FSMContext):
    # await state.set_state(ResumesInfoStates.waiting_for_list_contact)
    
    # for name, resume in enumerate(json.loads(resumes).items()):
    #     print('\n\n!!!\n\n', resume)
    #     result = await process_commitment(message, f'{resume[0]}: {resume[1]}', portrait)
    #     if result:
    #         await create_candidate(resume[1], portrait)
    #         id_of_candidate = await get_id_candidate_by_fio(resume[1].get('Имя'))
    #         try:
    #             data = await state.get_data()
    #             if "waiting_for_list_contact" not in data or data.get('waiting_for_list_contact') == None:
    #                 data["waiting_for_list_contact"] = [(resume[1].get('Телефон', ''), resume[1].get('Телеграм', ''), id_of_candidate)]
    #                 await state.set_data(data)
    #             else:
    #                 data['waiting_for_list_contact'].append((resume[1].get('Телефон', ''), resume[1].get('Телеграм', ''), id_of_candidate))
    #                 await state.set_data(data)

    #             # if data.get('waiting_for_list_contact') == None or not data.get('waiting_for_list_contact'):
    #             #     print('!!!!\n\n при пустом значении\n')
    #             #     await state.update_data(waiting_for_list_contact=[])
    #             #     data = await state.get_data()
    #             #     print('!!!! data', data['waiting_for_list_contact'])
    #             # contacts = data.get('waiting_for_list_contact', []).append((resume[1].get('Телефон', ''), resume[1].get('Телеграм', '')))
    #         except:
    #             print('ошибка при сохранении контактов')
    #             await message.answer(f"Ошибка при сохранении контактов. Процесс запустится повторно через 30 секунд.")
    #             await asyncio.sleep(30)
    #             await search_good_resumes(message, resumes, portrait, state)
            
    #         try:
    #             await message.answer(f"{resume[1].get('Телефон', '')}\n{resume[1].get('Телеграм', '')}")
    #         except:
    #             pass
    #         await message.answer(f"Резюме подходит под портрет: {resume}")

    #         # await state.update_data(waiting_for_list_contact=contacts)

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(process_commitment('Hi! How are you?'))
#     loop.close()

