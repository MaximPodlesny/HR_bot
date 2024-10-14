from aiogram.types import Message

async def format_start_message() -> str:
    """
    Formats the welcome message for the `/start` command.
    """
    return "Привет! Я HR-агент компании Catharsis, моя задача автоматизировать поиск и отбор кандидатов для ваших вакансий.\n\n" \
           "Чем могу помочь? Выберите вариант:\n" \
           "1. Создать вакансию\n" \
           "2. Добавить кандидата\n" \
           "3. Админ-панель"

async def format_create_vacancy_message() -> str:
    """
    Formats the message for creating a new vacancy.
    """
    return "Отлично! Давайте создадим новую вакансию. Пожалуйста, опишите вакансию максимально подробно. \n" \
           "Например:  \"Название вакансии: Frontend разработчик. Обязанности:  Разработка...  Требования: Опыт работы...  Условия: ...\""

async def format_vacancy_data(vacancy_data: Dict) -> str:
    """
    Formats vacancy data for confirmation.
    """
    return f"Название вакансии: {vacancy_data.get('title', 'Не указано')}\n" \
           f"Описание: {vacancy_data.get('description', 'Не указано')}\n" \
           f"Требования: {vacancy_data.get('requirements', 'Не указано')}\n" \
           f"Обязанности: {vacancy_data.get('responsibilities', 'Не указано')}"

async def format_add_candidate_message() -> str:
    """
    Formats the message for adding a candidate.
    """
    return "Введите ID вакансии, для которой вы хотите добавить кандидата.  \n" \
           "Или,  если вы хотите вручную ввести данные кандидата, введите 'manual'."

async def format_hh_search_results(candidates: List[Dict]) -> str:
    """
    Formats the results of the HH.ru search.
    """
    message = "Найденные кандидаты:\n\n"
    for index, candidate in enumerate(candidates, 1):
        message += f"{index}. {candidate.get('name', 'Имя не указано')}\n"
        message += f"    Профиль: {candidate.get('alternate_url', 'Ссылка не указана')}\n\n"
    return message

async def format_admin_panel_message() -> str:
    """
    Formats the message for the admin panel.
    """
    return "Добро пожаловать в админ-панель!\n\n" \
           "Выберите действие:\n" \
           "1. Управление вакансиями\n" \
           "2. Управление кандидатами\n" \
           "3. Просмотр отчетов"

async def format_manage_vacancies_message() -> str:
    """
    Formats the message for managing vacancies.
    """
    return "Управление вакансиями:\n\n" \
           "Выберите действие:\n" \
           "1. Просмотреть вакансии\n" \
           "2. Создать новую вакансию\n" \
           "3. Редактировать вакансию\n" \
           "4. Удалить вакансию"

async def format_manage_candidates_message() -> str:
    """
    Formats the message for managing candidates.
    """
    return "Управление кандидатами:\n\n" \
           "Выберите действие:\n" \
           "1. Просмотреть кандидатов\n" \
           "2. Фильтровать кандидатов по статусу, вакансии и т.д.\n" \
           "3. Обновить статус кандидата"

async def format_view_reports_message() -> str:
    """
    Formats the message for viewing reports.
    """
    return "Просмотр отчетов:\n\n" \
           "Выберите отчет:\n" \
           "1. Количество кандидатов по вакансиям\n" \
           "2. Прогресс кандидатов по этапам\n" \
           "3. Время, проведенное на каждом этапе"

async def send_notification(chat_id: int, message: str) -> None:
    """
    Sends a notification message to the specified chat ID.
    """
    await bot.send_message(chat_id, message)