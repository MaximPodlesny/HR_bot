from io import BytesIO
import json
import pypdf
from bot import bot
async def read_pdf_file(file_id):
    document_id = file_id  # Получаем ID документа
    file_info = await bot.get_file(document_id)  # Получаем информацию о файле
    file_path = file_info.file_path  # Получаем путь к файлу на сервере Telegram
    file_bytes = await bot.download_file(file_path)  # Скачиваем файл
    print('file_bytes - ', type(file_bytes))
    b_file = BytesIO(file_bytes.getvalue()) #file_bytes.getvalue() #BytesIO(file_bytes)
    print('b_file - ', type(b_file))
    # Преобразуем PDF в текст без сохранения файла
    pdf_reader = pypdf.PdfReader(b_file)
    # pdf_reader = pypdf.PdfReader(file_bytes.getvalue())
    
    print('pdf_reader - ', type(pdf_reader))

    # print('pdf_reader - ', type(pdf_reader))
    # try:
    #     print('pdf_reader.pages - ', type(pdf_reader.pages))
    # except:
    #     pass
    # try:
    #     print('pdf_reader.pages[0] - ', type(pdf_reader.pages[0]))
    # except:
    #     pass
    return [page.extract_text() for page in pdf_reader.pages]
    # return pages


# def pdf_to_text(file_id):
#     """Переводит содержимое PDF-файла в текст."""
#     file_bytes = get_file_bytes(file_id)  # Предполагается, что у вас есть функция get_file_bytes
#     file_stream = BytesIO(file_bytes)
#     pdf_reader = pypdf.PdfReader(file_stream)

#     all_text = ""
#     for page in pdf_reader.pages:
#         all_text += page.extract_text()

#     return all_text

def read(file_path):
    """Переводит содержимое PDF-файла в текст."""
    with open(file_path, "rb") as pdf_file:
        print(type(pdf_file))
        pdf_reader = pypdf.PdfReader(pdf_file)

        all_text = ""
        for page in pdf_reader.pages[:2]:
            all_text += page.extract_text()

        return all_text

if __name__ == '__main__':
    file_path = "resumes.pdf"
    text = read(file_path)
    print(text)