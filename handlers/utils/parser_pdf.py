from io import BytesIO
import json
import pypdf
from openai import AsyncOpenAI
from .get_file import read_pdf_file
from config import GPT_KEY

# async def read_pdf_file(file_id):
#     document_id = file_id  # Получаем ID документа
#     file_info = await bot.get_file(document_id)  # Получаем информацию о файле
#     file_path = file_info.file_path  # Получаем путь к файлу на сервере Telegram
#     file_bytes = await bot.download_file(file_path)  # Скачиваем файл

#     # Преобразуем PDF в текст без сохранения файла
#     pdf_reader = pypdf.PdfReader(BytesIO(file_bytes))
#     """Читает PDF-файл и возвращает список страниц."""
#     # with open(file_path, "rb") as pdf_file:
#     #     pdf_reader = pypdf.PdfReader(pdf_file)
#     #     pages = [page for page in pdf_reader.pages]
#     return pdf_reader.pages

async def made_structure_by_gpt(resumes, client):
    """Получает ответ от ChatGPT для обработки резюме."""
    prompt = """
    Я передаю тебе резюме. 
    Обработай резюме и выведи информацию в следующем json формате через запятую:

    Резюме № [номер резюме]:
    [Информация о резюме]

    Пример:

    Резюме № 1:
    Имя: Иван Иванов
    Телефон: +79991234567
    Телеграм: @IvanIvanov
    Почта: ivan.ivanov@example.com
    Опыт работы: 5 лет
    и так далее...
    """

    # response = await client.chat.completions.create(
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": resumes},
        ],
        response_format = {'type': "json_object"}
    )

    return response.choices[0].message.content

async def extract_resume_by_gpt(page, client):
    # print(page)
    prompt = "Ты  -  умный  и  дружелюбный  HR-бот. Ты получаешь часть текста от большого файла с большим количествам резюме.\
              **Твои  основные  задачи:**\
              *   **Определение начала и конца резюме:**  резюме может быть как на одной странице, так и на нескольких.\
              *   **Если ты получаешь страницу где есть начало резюме, но не понятно есть ли конец, тоесть нет начала следующего резюме:** ты записываешь в next_resume  начало резюме и вызываешь функцию 'give_first_resume()'.\
              *   **Если ты получаешь страницу где нет начала резюме, но не понятно есть ли конец, тоесть нет начала следующего резюме:** ты записываешь в аргумент middle_text резюме и вызываешь функцию вызываешь функцию 'give_middle_text()'.\
              *   **Если ты получаешь страницу где есть начало резюме и есть конец предыдущего резюме:** ты записываешь в аргумент next_resume конец предыдущего резюме, а в first_resume записываешь начало следующего резюме и вызываешь функцию 'give_next_resume()'.\
              *   **Если ты получаешь страницу где есть начало первого и есть начало следующего резюме:** ты записываешь в аргумент  first_resume первое резюме, а в next_resume записываешь начало следующего резюме и вызываешь функцию вызываешь функцию 'give_first_two_resumes()'.\
                **Дополнительные  инструкции:**\
              *   Предоставляй  четкие  и  понятные  инструкции ничего не придумывае, если не просят."

    tools = [
        {"type": "function",
         "function": {
                "name": "give_first_two_resumes",
                "description": "Записываешь в аргумент first_resume первое резюме, а в next_resume записываешь начало второго резюме.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_resume": {"type": "string"},
                        "next_resume": {"type": "string"},
                    },
                    "required": ["first_resume", "next_resume"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "give_first_resume",
                "description": "Отправляет текст первой часть резюме, когда не понятно есть ли в тексте конец резюме.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_text": {"type": "string"},
                    },
                    "required": ["first_resume"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "give_middle_text",
                "description": "Записываешь в middle_text текст резюме, когда в тексте нет начала резюме и нет начала следующего резюме.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "middle_text": {"type": "string"},
                    },
                    "required": ["middle_text"],
                },
            },
        },
        {"type": "function",
         "function": {
                "name": "give_next_resume",
                "description": "Записывает в аргумент first_resume конец предыдущего резюме, а в next_resume записывает начало следующего резюме.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "first_resume": {"type": "string"},
                        "next_resume": {"type": "string"},
                    },
                    "required": ["first_resume", "next_resume"],
                },
            },
        },
    ]
    response = await client.chat.completions.create(
        model= "gpt-4o-mini", #"gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": prompt,
            },
            {
            "role": "user",
            "content": page,
            },
        ],
        tools=tools
    )

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
        
        if function_name == "give_first_resume":
            print('!!!! give_ferst_resume')
            return arguments.get('first_resume', ''), '', '', ''
        elif function_name == "give_middle_text":
            print('!!!! give_middle_resume')
            return '', arguments.get("middle_text", ''), '', ''
        elif function_name == "give_next_resume":
            print('!!!! give_next_resume')
            return '', '', arguments.get("next_resume", ''), arguments.get("first_resume", '')
        elif function_name == "give_first_two_resumes":
            print('!!!! give_first_two_resumes')
            return arguments.get("first_resume", 'функция give_next_resume накосячила first_resume'), '',  arguments.get("next_resume", 'функция give_next_resume накосячила next_resume'), ''
 
    else:
        return response.choices[0].message.content

async def create_lis_resume(pages, client):
    
    """Создаёт список резюме."""
    resume_text_list = []

    if "резюме" in pages[0].extract_text().lower() or ("имя" in pages[0].extract_text().lower() and "фамилия" in pages[0].extract_text().lower()):
        resume_text = ""
        flag = False
        for page in pages:
            middle_text = page.extract_text()
            if "резюме" in resume_text.lower() or ("имя" in resume_text.lower() and "фамилия" in resume_text.lower()):
                flag = True
                resume_text += middle_text
            elif ("резюме" not in resume_text.lower() or ("имя" not in resume_text.lower() and "фамилия" not in resume_text.lower())) and flag:
                resume_text += middle_text
            elif ("резюме" in resume_text.lower() or ("имя" in resume_text.lower() and "фамилия" in resume_text.lower())) and flag:
                flag = False
                resume_text_list.append(resume_text)
                resume_text = middle_text
    else:
        resume = ''
        flag = False
        for page in pages:
            middle_text = page.extract_text()
            first_resume, middle_text, next_resume, end_resume = await extract_resume_by_gpt(middle_text, client)
            print()
            print('first_resume - ', first_resume)
            print()
            print('next_resume - ', next_resume)
            if end_resume:
                print('in fierst condition')
                resume += end_resume
                resume_text_list.append(resume)
                resume = next_resume
                flag = False
            elif (first_resume and not next_resume and not flag) or middle_text:
                print('in second condition')
                if middle_text:
                    resume += middle_text
                else:
                    resume += first_resume
                # resume += next_resume
                flag = True
            elif first_resume and not next_resume and flag:
                print('in thitd condition')
                resume_text_list.append(resume)
                resume += first_resume
                # resume += next_resume
            elif first_resume and next_resume and flag:
                print('in thitd condition')
                resume_text_list.append(resume)
                resume += first_resume
                resume_text_list.append(resume)
                resume += next_resume
                flag = False
            elif first_resume and next_resume:
                print('in forth condition')
                resume += first_resume
                resume_text_list.append(resume)
                resume = next_resume

    return resume_text_list

async def parser(file_id):
    client = AsyncOpenAI(api_key=GPT_KEY)
    # file_path = "resumes.pdf"
    pages = await read_pdf_file(file_id)
    # list_resumes = await create_lis_resume(pages, client)
    resumes_text = ' '.join(pages)
    # for resume_text in list_resumes:
    list_structured_resumes = await made_structure_by_gpt(resumes_text, client)
    print(list_structured_resumes[:600])
        # list_structured_resumes.append(structured_resume)
    return list_structured_resumes

   
