import asyncio
from handlers.search_candidate import search_c
from handlers.utils.candidate import collect_candidate_info
# from openai import OpenAI, AsyncOpenAI
# from config import GPT_KEY

# # openai.api_key = GPT_KEY 
# # client = OpenAI(api_key=GPT_KEY)
# client = AsyncOpenAI(api_key=GPT_KEY)
# async def process_commitment(message):

#     prompt = f"Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание.  Ты  интегрирован  с  API  HeadHunter,  Bitrix24  и  OpenAI.\
#               **Твои  основные  задачи:**\
#               *   **Поиск  вакансий:**  Помоги  пользователям  найти  вакансии  на  HeadHunter  по  ключевым  словам.\
#               *   **Отправка  резюме:**  Помоги  пользователям  отправить  резюме  на  вакансии  через  HeadHunter  или  Bitrix24.\
#               *   **Создание  лидов  в  Bitrix24:**  Создавай  новые  лиды  в  Bitrix24  для  кандидатов,  которые  связались  с  ботом.\
#               *   **Генерация  вопросов  для  собеседования:**  Используй  OpenAI  для  генерации  релевантных  вопросов  для  собеседования  на  основе  описания  вакансии  и  требований.\
#               *   **Анализ  ответов  кандидата:**  Используй  OpenAI  для  анализа  ответов  кандидата  на  вопросы  собеседования.\
#               *   **Генерация  тестовых  заданий:**  Используй  OpenAI  для  генерации  тестовых  заданий  для  кандидатов.\
#               *   **Администрирование:**  Предоставь  администратору  доступ  к  панели  управления  вакансиями,  кандидатами  и  отчетами.\
#               **Дополнительные  инструкции:**\
#               *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
#               *   Предоставляй  четкие  и  понятные  инструкции.\
#               *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации.\
#               *   Обрабатывай  ошибки  и  предоставляй  пользователям  информативные  сообщения  об  ошибках."

#     response = await client.chat.completions.create(
#       model="gpt-3.5-turbo",
#       messages=[
#         {
#         "role": "user",
#         "content": message,
#         }
#       ],
#       max_tokens=1500
#     )
#     return response.choices[0].message.content
    # print(response)


from g4f.client import Client
import g4f
client = Client()

async def process_commitment(message):
  prompt = "Ты  -  умный  и  дружелюбный  HR-бот,  который  помогает  пользователям  найти  вакансии,  отправить  резюме,  пройти  собеседование  и  получить  тестовое  задание.  Ты  интегрирован  с  API  HeadHunter,  Bitrix24  и  OpenAI.\
              **Твои  основные  задачи:**\
              *   **Поиск  кандидатов на вакансию:**  Помоги  найти кандидаов на вакансии  через  HeadHunter  или собственную базу резюме.\
              *   **Если ты получаешь недостаточно информации о кандидате(Каким вы видите идеального кандидата?, Пол / возраст / минимальный опыт?, Какие у него должны быть качества?, Какими навыками должен обладать?), необходимо вызвать функцию 'collect_candidate_info()'\
              *   **Применение функций:**  Для выполнения поставленных задачь обязательно применяй следующие функции: 'search_c()' - для составления портрета кандидата, 'create_vacancy()' - для создания вакансии на HeadHunter.\
              *   **Отправка  вакансии:**  Помоги  отправить вакансию  на  HeadHunter  или  Bitrix24.\
              *   **Создание  лидов  в  Bitrix24:**  Создавай  новые  лиды  в  Bitrix24  для  кандидатов,  которые  связались  с  ботом.\
              *   **Генерация  вопросов  для  собеседования:**  Используй  OpenAI  для  генерации  релевантных  вопросов  для  собеседования  на  основе  описания  вакансии  и  требований.\
              *   **Анализ  ответов  кандидата:**  Используй  OpenAI  для  анализа  ответов  кандидата  на  вопросы  собеседования.\
              *   **Генерация  тестовых  заданий:**  Используй  OpenAI  для  генерации  тестовых  заданий  для  кандидатов.\
              *   **Администрирование:**  Предоставь  администратору  доступ  к  панели  управления  вакансиями,  кандидатами  и  отчетами.\
              **Дополнительные  инструкции:**\
              *   Будь  вежлив  и  дружелюбен  в  общении  с  пользователями.\
              *   Предоставляй  четкие  и  понятные  инструкции.\
              *   Используй  форматирование  текста  для  лучшего  визуального  представления  информации.\
              *   Обрабатывай  ошибки  и  предоставляй  пользователям  информативные  сообщения  об  ошибках."
  response = await client.chat.completions.async_create(
      model= g4f.models.gpt_4o_mini,  #"gpt-3.5-turbo",
      messages=[
         {"role": "system", "content": prompt},
         {"role": "user", "content": message}
         ],
        #  functions=[
        #     {
        #         "name": "collect_candidate_info",
        #         "description": "Собирает информацию о кандидате на вакансию.",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "a": {"type": "integer"},
        #                 "b": {"type": "integer"},
        #             },
        #             "required": ["a", "b"],
        #         },
        #     }
          # ]      # Add any other necessary parameters
  )
  # if response.choices[0].message.function_call:
  #      # Получение аргументов функции
  #     #  function_args = response.choices[0].message.function_call.arguments

  #      # Вызов функции
  #      result = await collect_candidate_info()

  #      # Отправка ответа ChatGPT
  #      response = await client.chat.completions.async_create(
  #         model= g4f.models.gpt_4o_mini,
  #         messages=[
  #             {"role": "system", "content": prompt},
  #             {"role": "user", "content": message},
  #             {"role": "function", "name": "calculate_sum", "content": result},
  #         ],
  #      )

  # await message.answer(response.choices[0].message.content)
  return response.choices[0].message.content

async def main():
  messages = []
  while True:
    message = input()
    messages.append({"role": "user", "content": message})
    resp = await process_commitment(message)
    print(resp)
    messages.append({"role": "assistant", "content": resp})
    

if __name__ == '__main__':
    # process_commitment('message')
    asyncio.run(main())

