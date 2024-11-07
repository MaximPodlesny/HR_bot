
from pypdf import PdfWriter, PdfReader, PageObject


from fpdf import FPDF
def create_pdf_from_resumes(resumes, output_filename="resumes.pdf"):
    """Создает PDF-файл из списка резюме."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, resume in enumerate(resumes):
        pdf.cell(200, 10, txt=f"Резюме № {i + 1}", ln=True, align='L')
        resume_bytes = resume.encode("utf-8")  # Преобразуем в байтовый объект
        pdf.multi_cell(200, 5, txt=resume_bytes.decode("latin-1"), align='L')  # Преобразуем обратно в строку

    pdf.output(output_filename)
# def create_pdf_from_resumes(resumes, output_filename="resumes.pdf"):
#     """Создает PDF-файл из списка резюме."""
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)

#     for i, resume in enumerate(resumes):
#         pdf.add_page()
#         pdf.set_font("Arial", "B", 16)
#         pdf.cell(0, 10, f"Резюме № {i + 1}", align="C")
#         pdf.ln(10)
#         pdf.set_font("Arial", "", 12)
#         pdf.multi_cell(0, 5, resume)

#     pdf.output(output_filename)

import io

# def create_pdf_from_resumes(resumes, output_filename="resumes.pdf"):
#     """Создает PDF-файл из списка резюме."""
#     pdf_writer = PdfWriter()

#     for i, resume in enumerate(resumes):
#         # Создаем новую страницу
#         page = PageObject.create_blank_page(width=612, height=792)  # Используем пустую страницу из существующего PDF (или создайте новую)
#         pdf_writer.add_page(page)

#         # Добавляем текст резюме на страницу
#         page.extract_text()  # Удаляем существующий текст
#         page.add_content(f"Резюме № {i + 1}nn{resume}")

#     # Сохраняем PDF-файл
#     pdf_bytes = io.BytesIO()
#     pdf_writer.write(pdf_bytes)
#     with open(output_filename, "wb") as output_file:
#         output_file.write(pdf_bytes.getvalue())

# Список резюме (замените на ваши данные)
resumes = [
    """
    Имя: Иван Иванов
    Контакты:
    * Телефон: +7 (999) 123-45-67
    * Почта: ivan.ivanov@example.com
    * LinkedIn: [ссылка на профиль]
    Опыт работы:
    * Менеджер по продажам, ООО "Компания", Москва, 2020 - настоящее время
        * Достижение плановых показателей продаж на 120%.
        * Разработка и внедрение новых маркетинговых стратегий.
        * Управление командой из 5 сотрудников.
    * Специалист по продажам, ООО "Фирма", Москва, 2018 - 2020
        * Увеличение объема продаж на 15% за период работы.
        * Участие в разработке и проведении маркетинговых акций.
    Образование:
    * Московский государственный университет, Факультет экономики, Специальность: Экономика, 2014 - 2018
    Навыки:
    * Продажи
    * Маркетинг
    * Управление командой
    * MS Office
    * Английский язык (уровень B2)
    Дополнительная информация:
    * Обладаю высокой мотивацией и стремлением к развитию.
    * Ответственный и целеустремленный сотрудник.
    """,
    '''## Резюме №2

    **Имя:**  Анна  Петрова

    **Контакты:**

    *   Телефон: +7 (900) 111-22-33
    *   Почта: anna.petrova@example.com
    *   GitHub: [ссылка на профиль]

    **Опыт работы:**

    *   **Веб-разработчик**,  **ООО "Студия"**,  **Санкт-Петербург**,  **2019 - настоящее время**
        *   Разработка  и  поддержка  веб-сайтов  и  веб-приложений.
        *   Использование  технологий  HTML,  CSS,  JavaScript,  React.
        *   Участие  в  проектах  по  разработке  API  и  интеграции  с  третьими  сторонами.
    *   **Фрилансер**,  **2017 - 2019**
        *   Разработка  веб-сайтов  и  веб-приложений  для  частных  лиц  и  компаний.

    **Образование:**

    *   **Санкт-Петербургский  государственный  университет**,  **Факультет  прикладной  математики  и  процессов  управления**,  **Специальность:  Прикладная  математика**,  **2015 - 2019**

    **Навыки:**

    *   HTML
    *   CSS
    *   JavaScript
    *   React
    *   Node.js
    *   Git
    *   Английский  язык (уровень  B1)

    **Дополнительная  информация:**

    *   Увлечена  веб-разработкой  и  слежу  за  новейшими  технологиями.
    *   Имею  опыт  работы  в  команде  и  самостоятельно.''',
    '''## Резюме №3

    **Имя:**  Дмитрий  Сидоров

    **Контакты:**

    *   Телефон: +7 (911) 111-11-11
    *   Почта: dmitry.sidorov@example.com
    *   Telegram: [ссылка на профиль]

    **Опыт работы:**

    *   **Data  Scientist**,  **ООО "Лаборатория"**,  **Москва**,  **2021 - настоящее время**
        *   Разработка  и  внедрение  моделей  машинного  обучения  для  решения  бизнес-задач.
        *   Анализ  больших  данных  с  помощью  Python,  Pandas,  Scikit-learn.
        *   Визуализация  данных  с  помощью  matplotlib  и  seaborn.
    *   **Аналитик  данных**,  **ООО "Компания"**,  **Москва**,  **2019 - 2021**
        *   Анализ  данных  для  выявления  трендов  и  паттернов.
        *   Подготовка  отчетов  и  презентаций  для  руководства.

    **Образование:**

    *   **Московский  физико-технический  институт**,  **Факультет  прикладной  математики  и  физики**,  **Специальность:  Прикладная  математика**,  **2016 - 2021**

    **Навыки:**

    *   Python
    *   Pandas
    *   Scikit-learn
    *   Matplotlib
    *   Seaborn
    *   SQL
    *   Английский  язык (уровень  B2)

    **Дополнительная  информация:**

    *   Имею  опыт  работы  с  различными  наборами  данных  и  моделями  машинного  обучения.
    *   Увлечен  анализом  данных  и  искусственным  интеллектом.''',
    '''## Резюме №4

    **Имя:**  Екатерина  Иванова

    **Контакты:**

    *   Телефон: +7 (921) 123-45-67
    *   Почта: ekaterina.ivanova@example.com
    *   Instagram: [ссылка на профиль]

    **Опыт работы:**

    *   **SMM-менеджер**,  **ООО "Агентство"**,  **Санкт-Петербург**,  **2020 - настоящее время**
        *   Разработка  и  реализация  стратегий  SMM  для  клиентов.
        *   Ведение  социальных  сетей  (Instagram,  Facebook,  VK).
        *   Создание  контента  и  рекламных  кампаний.
        *   Анализ  статистики  и  отслеживание  результатов.
    *   **Контент-менеджер**,  **ООО "Компания"**,  **Санкт-Петербург**,  **2018 - 2020**
        *   Создание  и  публикация  контента  для  веб-сайта  и  социальных  сетей.
        *   Работа  с  системами  управления  контентом ...'''
]
resumes = [
    """
    ## Resume №1

**Name:** Ivan Ivanov

**Contact Information:**

*   Phone: +7 (999) 123-45-67
*   Email: ivan.ivanov@example.com
*   LinkedIn: [link to profile]

**Work Experience:**

*   **Sales Manager**,  **OOO "Company"**,  **Moscow**,  **2020 - Present**
    *   Achieved 120% of planned sales targets.
    *   Developed and implemented new marketing strategies.
    *   Managed a team of 5 employees.
*   **Sales Specialist**,  **OOO "Firma"**,  **Moscow**,  **2018 - 2020**
    *   Increased sales volume by 15% during the period of work.
    *   Participated in the development and implementation of marketing campaigns.

**Education:**

*   **Moscow State University**,  **Faculty of Economics**,  **Major: Economics**,  **2014 - 2018**

**Skills:**

*   Sales
*   Marketing
*   Team Management
*   MS Office
*   English (B2 level)

**Additional Information:**

*   I am highly motivated and eager to learn.
*   I am a responsible and goal-oriented employee.
    """,
    '''## Resume №2

**Name:** Anna Petrova

**Contact Information:**

*   Phone: +7 (900) 111-22-33
*   Email: anna.petrova@example.com
*   GitHub: [link to profile]

**Work Experience:**

*   **Web Developer**,  **OOO "Studio"**,  **Saint Petersburg**,  **2019 - Present**
    *   Developing and maintaining websites and web applications.
    *   Using technologies such as HTML, CSS, JavaScript, React.
    *   Participating in projects involving API development and integration with third-party services.
*   **Freelancer**,  **2017 - 2019**
    *   Developing websites and web applications for individuals and companies.

**Education:**

*   **Saint Petersburg State University**,  **Faculty of Applied Mathematics and Control Processes**,  **Major: Applied Mathematics**,  **2015 - 2019**

**Skills:**

*   HTML
*   CSS
*   JavaScript
*   React
*   Node.js
*   Git
*   English (B1 level)

**Additional Information:**

*   Passionate about web development and keeping up with the latest technologies.
*   Experienced in working both in a team and independently.''',
    '''## Resume №3

**Name:** Dmitry Sidorov

**Contact Information:**

*   Phone: +7 (929) 838-38-64
*   Email: dmitry.sidorov@example.com
*   Telegram: [link to profile]

**Work Experience:**

*   **SMM Manager**,  **OOO "Agency"**,  **Saint Petersburg**,  **2020 - Present**
    *   Developing and implementing SMM strategies for clients.
*   **Data Analyst**,  **OOO "Company"**,  **Moscow**,  **2019 - 2021**
    *   Analyzing data to identify trends and patterns.
    *   Preparing reports and presentations for management.

**Education:**

*   **Moscow Institute of Physics and Technology**,  **Faculty of Applied Mathematics and Physics**,  **Major: Applied Mathematics**,  **2016 - 2021**

**Skills:**

*   Python
*   Pandas
*   Scikit-learn
*   Matplotlib
*   Seaborn
*   SQL
*   English (B2 level)

**Additional Information:**

*   Experienced in working with various datasets and machine learning models.
*   Passionate about data analysis and artificial intelligence.''',
    '''## Resume №4

**Name:** Ekaterina Ivanova

**Contact Information:**

*   Phone: 8 (989) 819-80-15
*   Email: ekaterina.ivanova@example.com
*   Instagram: [link to profile]

**Work Experience:**

*   **SMM Manager**,  **OOO "Agency"**,  **Saint Petersburg**,  **2020 - Present**
    *   Developing and implementing SMM strategies for clients.
    *   Managing social media accounts (Instagram, Facebook, VK).
    *   Creating content and advertising campaigns.
    *   Analyzing statistics and tracking results.
*   **Content Manager**,  **OOO "Company"**,  **Saint Petersburg**,  **2018 - 2020**
    *   Creating and publishing content for the website and social media.
    *   Working with content management systems (CMS).

**Education:**

*   **Saint Petersburg State University**,  **Faculty of Journalism**,  **Major: Journalism**,  **2014 - 2018**

**Skills:**

*   SMM
*   Social Media
*   Content Marketing
*   Copywriting
*   Graphic...'''
]

if __name__ == '__main__':
    # Создание PDF-файла
    create_pdf_from_resumes(resumes*12)
