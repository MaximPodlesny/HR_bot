import requests
import json
from datetime import datetime

# --- Замените на свои данные ---
BITRIX_URL = "YOUR_BITRIX_URL" # Ваш URL Битрикс24, например: 'https://yourcompany.bitrix24.ru'
BITRIX_TOKEN = "YOUR_BITRIX_TOKEN" # Ваш токен доступа
KANBAN_ENTITY_TYPE_ID = 1 # 1 - для лидов, 2 - для сделок, ...
# --- Статусы лида ---
STATUS_BEFORE_INTERVIEW = "BEFORE_INTERVIEW" #Код статуса до интервью
STATUS_AFTER_INTERVIEW = "AFTER_INTERVIEW" #Код статуса после интервью
# --- Установка базового URL ---
REST_API_BASE_URL = f"{BITRIX_URL}/rest/1/"

def bitrix_api_request(method, params=None, method_type='post'):
    """Выполняет запрос к REST API Битрикс24."""
    url = f"{REST_API_BASE_URL}{method}"
    headers = {'Authorization': f'Bearer {BITRIX_TOKEN}'}
    try:
        if method_type == 'post':
             response = requests.post(url, headers=headers, json=params)
        else:
            response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к Битрикс24 API: {e}")
        return None

def create_kanban_board(board_name):
    """Создает канбан-доску."""
    method = "crm.kanban.kanban.add"
    params = {
        "NAME": board_name,
        "ENTITY_TYPE_ID": KANBAN_ENTITY_TYPE_ID,
        "FIELDS": [
            {"NAME": "STATUS_ID", "TYPE": "LIST", "LIST": [
                { "ID": STATUS_BEFORE_INTERVIEW, "NAME": "До интервью" },
                { "ID": STATUS_AFTER_INTERVIEW, "NAME": "После интервью" }
            ]}
        ]
    }
    response = bitrix_api_request(method, params)
    if response and 'result' in response:
        return response['result']['ID']
    else:
        print(f"Ошибка при создании доски: {response}")
        return None

def create_lead(board_id, lead_name, initial_status=STATUS_BEFORE_INTERVIEW, additional_data=None):
    """Создает лид на канбан-доске."""
    method = "crm.kanban.item.add"
    params = {
        "KANBAN_ID": board_id,
        "FIELDS": {
             "TITLE": lead_name,
             "STATUS_ID": initial_status,
            }.update(additional_data if additional_data else {})
        }
    response = bitrix_api_request(method, params)
    if response and 'result' in response:
        return response['result']['ID']
    else:
       print(f"Ошибка при создании лида: {response}")
       return None

def move_lead_to_status(board_id, lead_id, new_status):
    """Перемещает лид на канбан-доске в другой статус."""
    method = "crm.kanban.item.update"
    params = {
        "KANBAN_ID": board_id,
        "ID": lead_id,
        "FIELDS": {
            "STATUS_ID": new_status
        }
    }
    response = bitrix_api_request(method, params)
    if response and response.get('result', False) == True: #Проверка результата для update метода
        return True
    else:
        print(f"Ошибка при перемещении лида: {response}")
        return False

def get_kanban_board(board_name):
    """Получает канбан-доску по имени."""
    method = "crm.kanban.kanban.list"
    params = {"filter": {"NAME": board_name, "ENTITY_TYPE_ID": KANBAN_ENTITY_TYPE_ID}}
    response = bitrix_api_request(method, params, method_type='get')
    if response and 'result' in response and response['result']:
        return response['result'][0]['ID']
    else:
        print(f"Доска с именем '{board_name}' не найдена или ошибка: {response}")
        return None

if __name__ == "__main__":
    # --- Пример использования ---
    board_name = "Кандидаты на вакансию Python разработчик"
    board_id = get_kanban_board(board_name)
    if not board_id:
      board_id = create_kanban_board(board_name)

    if board_id:
        lead_name = "Иванов Иван"
        lead_id = create_lead(board_id, lead_name, STATUS_BEFORE_INTERVIEW, {"UF_CRM_1703400737": '2023-12-24'}) # Добавил доп. поле "UF_CRM_1703400737"
        if lead_id:
            print(f"Лид '{lead_name}' с ID {lead_id} успешно создан.")
            if move_lead_to_status(board_id, lead_id, STATUS_AFTER_INTERVIEW):
                print(f"Лид '{lead_name}' успешно переведен в статус 'После интервью'.")
            else:
                print(f"Не удалось перевести лид '{lead_name}' в статус 'После интервью'.")
        else:
            print(f"Не удалось создать лид '{lead_name}'.")
    else:
        print(f"Не удалось создать или получить доску '{board_name}'.")