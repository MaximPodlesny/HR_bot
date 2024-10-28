import asyncio
import json
from openai import OpenAI, AsyncOpenAI
from config import GPT_KEY
from aiogram import types
# from dotenv import load_dotenv

# load_dotenv()


client = AsyncOpenAI(api_key=GPT_KEY)
async def process_commitment(message: types.Message, resume, portrait):
# async def process_commitment(pr):

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти подходящих кандидатов на вакансию.\
              **Твоя  задача:**\
              *   **Проанализировать резюме:** ты получаешь портрет кандидата и резюме и тебе надо разобраться подходит ли резюме под портрет кандидата.\
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
    
async def search_good_resumes(message: types.Message, resumes, portrait):
    for name, resume in enumerate(json.loads(resumes).items()):
        result = await process_commitment(message, f'{resume[0]}: {resume[1]}', portrait)
        if result:
            await message.answer(f"Резюме подходит под портрет: {resume}")
            await message.answer(f"Резюме подходит под портрет: {result}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_commitment('Hi! How are you?'))
    loop.close()

