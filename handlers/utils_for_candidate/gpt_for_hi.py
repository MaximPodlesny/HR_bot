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
async def process_hi(message: types.Message, resp):
# async def process_commitment(pr):

    prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  пройти электронное собеседование на вакансию.\
              **Твоя  задача:**\
              *   **Если в переписки нет приветствия** приветствие в формате: Еще раз спасибо за отклик {имя кандидата}! Я bot-помощник HR для отбора кандидатов на позицию {название позиции}, то поприветствуй кандидата в приведенном формате\
              *   **Если в переписке есть приветствие в формате: Еще раз спасибо за отклик {имя кандидата}! Я bot-помощник HR для отбора кандидатов на позицию {название позиции}:** возвращаешь только слово 'да'\
              **Дополнительные  инструкции:**\
              *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
              *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывае, если не просят.\
              *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации."
    # prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти подходящих кандидатов на вакансию.\
    #           **Твоя  задача:**\
    #           *   **Проанализировать ответы:** ты получаешь вопросы и ответы кандидата на эти вопросы.\
    #           *   **Если правильных ответов более 79%:** вызвать функцию 'order()'\
    #           *   **Если правильных ответов менее 79%:** вызвать функцию 'reject()'              *   **Если в переписки нет приветствия** приветствие в формате: еще раз спасибо за отклик {имя кандидата}! я помощник hr для отбора кандидатов на позицию {название позиции}, то поприветствуй кандидата в приведенном формате и добавь это - Формат собеседования будет следующий: 1. расскажу вам о компании 2. попрошу вас ответить на важные вопросы 3. Отправлю тестовое задание, если оно есть 4. мы пообщаемся и я смогу ответить на ваши вопросы о вакансии. Если все понятно, напиши - поехали.\

    
    # tools = [
    #     {"type": "function",
    #      "function": {
    #             "name": "order",
    #             "description": "Приглашает к следующему этапу.",
    #             # "parameters": {
    #             #     "type": "object",
    #             #     "properties": {
    #             #         "resume": {"type": "string"},
    #             #     },
    #             #     "required": ["resume"],
    #             # },
    #         },
    #     },
    #     {"type": "function",
    #      "function": {
    #             "name": "reject",
    #             "description": "Отказ.",
    #             # "parameters": {
    #             #     "type": "object",
    #             #     "properties": {
    #             #         "resume_off": {"type": "string"},
    #             #     },
    #             #     "required": ["resume_off"],
    #             # },
    #         },
    #     },
    # ]

    response = await client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
        "role": "system",
        "content": prompt,
        },
      ] + resp,
    #   tools=tools
        # max_tokens=3000
      )
#     answer = response.choices[0].message.content
# # *3.  Обработка  ответа  ChatGPT:**
#     print(response.choices[0].message.content)
#     arguments_object = ''
#     try:
#         tool_call = response.choices[0].message.tool_calls[0]
#         arguments_object = tool_call.function.arguments
#     except:
#         pass
    
#     # if response.choices[0].message.content == "function_call":
#     if response.choices[0].message.content == None and arguments_object:
        
#         # arguments = json.loads(arguments_object)
#         print('!!!! в функции gpt')
#         # function_call = response.choices[0].message.function_call
#         function_name = tool_call.function.name
        
#         if function_name == "order":
#             print('!!!! order')
#             await message.answer('Order')
#             await order(meesage, state)
            
#         elif function_name == "reject":
#             print('!!!! reject')
#             await message.answer('Reject')
#             return ''
#     else:
    return response.choices[0].message.content