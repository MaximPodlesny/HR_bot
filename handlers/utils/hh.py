import asyncio
import json
import os
import subprocess
from bs4 import BeautifulSoup
import psutil
from requests_oauthlib import OAuth2Session
import requests
from time import sleep
from fake_useragent import UserAgent
from config import message_for_hh
from handlers.utils.candidate import create_candidate, get_id_candidate_by_fio
from handlers.utils.ids_from_db import get_ids_vacancies

sess = requests.Session()
# sess.verify = False
with open('I:\Projects Python\HR_bot\config_hh.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    global client_id
    client_id = config.get('client_id')
    global client_secret
    client_secret = config.get('client_secret')
    global token
    token = config.get('token')
    global refresh_token
    refresh_token = config.get('refresh_token')

def get_token():
    authorization_base_url = 'https://hh.ru/oauth/authorize'
    token_url = 'https://api.hh.ru/token'

    oauth = OAuth2Session(client_id)

    # 1. Запрос авторизации
    authorization_url, state = oauth.authorization_url(authorization_base_url)

    # 2. Перенаправление пользователя на страницу авторизации
    print('Перейдите по этой ссылке, чтобы авторизоваться:', authorization_url)

    # 3. Получение кода авторизации
    authorization_response = input('Введите код авторизации: ')

    # 4. Получение токена
    ask_to_server(sess, authorization_response)

def refr_token(refresh_token):
    authorization_base_url = 'https://hh.ru/oauth/authorize'
    token_url = 'https://api.hh.ru/token'

    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': UserAgent().chrome,
    }

    data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_id": client_id,
    "client_secret": client_secret
    }

    # Отправка запроса
    response = requests.post(token_url, data=data, headers=headers)

    # Обработка ответа
    if response.status_code == 200:
        # Получение нового токена
        token_data = response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        print(f"Новый access_token: {access_token}")
        with open('I:\Projects Python\HR_bot\config_hh.json', 'w', encoding='utf-8') as f:
            config = {"client_id": client_id,
                      "client_secret": client_secret,
                      "token": access_token,
                      "refresh_token": refresh_token
                      }
            json.dump(config, f, indent=4)
            
        current_pid = os.getpid()
        subprocess.run([r'I:\Projects Python\HR_bot\venv\Scripts\python', 'main.py'])  
        process = psutil.Process(current_pid)
        # Завершаем процесс
        process.terminate()
    else:
        print(f"Ошибка получения токена: {response.text}")

def xsrf(text):
    bs = BeautifulSoup(text, 'html5lib')
    xsrf = bs.find('input', {'name': "_xsrf", 'type': "hidden"})['value']
    print('\n\n!!!\n\n', xsrf)
    return xsrf

def get_outh(sess):
    text = sess.get('https://almaty.hh.kz/account/login', headers={'User-Agent': UserAgent().chrome}).text
    post = sess.post(
        'https://almaty.hh.kz/account/login',
        data={
            'username': 's.mishcheryakov@catharsis.kz',
            'password': 'Catharsis2024',
            'remember': 'yes',
            '_xsrf': xsrf(text)
        },
        allow_redirects=False,
        headers={'User-Agent': UserAgent().chrome}
    )
    # resp = sess.post('https://almaty.hh.kz/account/login', data={'username': 's.mishcheryakov@catharsis.kz', 'password': 'Catharsis2024'}, headers={'User-Agent': UserAgent().chrome})
    print(json.loads(post.text)["recaptcha"]["siteKey"], sess)
    return json.loads(post.text)["recaptcha"]["siteKey"]

def ask_to_server(sess, code):
    headers = {
        'Accept': 'application/x-www-form-urlencoded',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': UserAgent().chrome,
    }
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }
    resp = sess.post('https://api.hh.ru/token', headers=headers, data=data)
    with open('token.txt', 'w', encoding='utf-8') as f:
        print(resp.json(), file=f)
    print(resp.json())

def get_areas(sity):
    resp = sess.get('https://api.hh.ru/areas', headers={'User-Agent': UserAgent().chrome})
    data = [s for d in resp.json() for s in d['areas'] if (s['name']).lower() == sity.lower()]
    if resp.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    try:
        return data[0]['id']
    except:
        raise IndexError()
    # with open('areas.txt', 'w', encoding='utf-8') as f:
    #     print(data, file=f)


def get_professional_roles():
    resp = sess.get('https://api.hh.ru/professional_roles', headers={'User-Agent': UserAgent().chrome})
    data = [{'id': s['id'], 'name': s['name']} for d in resp.json()['categories'] for s in d['roles']]
    if resp.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    return data
    # with open('professional_roles.txt', 'w', encoding='utf-8') as f:
    #     print(data, file=f)


# def get_vacancies(sess):
#     post = sess.get(
#         'https://almaty.hh.kz/employer/vacancies/drafts?hhtmFrom=vacancy_create&hhtmFromLabel=header',
#         # data={
#         #     'username': 's.mishcheryakov@catharsis.kz',
#         #     'password': 'Catharsis2024',
#         #     'remember': 'yes',
#         #     '_xsrf': xsrf(text)
#         # },
#         allow_redirects=False,
#         headers={'User-Agent': UserAgent().chrome}
#     )
#     # with open('hh.txt', 'w', encoding='utf-8') as f:
#     #     print(post.text, file=f)
#     print(post.text)

async def creat_vacancy(message, state, name, description, area, professional_roles,
                        token=token,
                        sess=sess,
                        type={'id': 'open'},
                        billing_type={'id': 'standard_plus'},
                        employment=None,
                        salary=None,
                        experience=None):
    print('\n\n in create_vacancy\n\n')
    print(f'\n\nemployment= {employment}\nsalary={salary}\nexperience={experience}\n')

    # if employment:
    #     employment = employment['id']
    # if experience:
    #     experience = experience['id']

    post = sess.post(
        'https://api.hh.ru/vacancies',
        data=json.dumps({
            'type': type,
            'name': name,
            'description': description,
            'billing_type': billing_type,
            'area': area,
            'professional_roles': professional_roles,
            'employment': employment,
            'salary': salary,
            'experience': experience,
        }),
        allow_redirects=False,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': UserAgent().chrome}
    )
    if post.status_code == 403:
        print(f'\n\n!!!!\n\n geting new access_token\n{post}')
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    return post

# Функция для получения списка вакансий с HH.ru
async def get_vacancies_from_hh():
    url = 'https://api.hh.ru/employers/2915213/vacancies/active'
    headers = {'Authorization': f'Bearer {token}'}
    response = sess.get(url, headers=headers)
    print('\n\n in get_vacancies_from_hh\n\n')
    if response.status_code == 200:
        vacancies_data = response.json()
        # print('vacancies_data', vacancies_data['items'])
        return vacancies_data['items']
    elif response.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    else:
        print(f"Ошибка получения вакансий: {response.status_code}")
        return []

# Функция для получения откликов на вакансию
async def get_responses_for_vacancy(vacancy_id):
    print('\n\n in get_responses_for_vacancy\n\n')
    url = f'https://api.hh.ru/negotiations/response'
    headers = {'Authorization': F'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': UserAgent().chrome}
    data = {
        'vacancy_id': vacancy_id,
        'status': 'active'
    }
    response = sess.get(url, params=data, headers=headers)
    if response.status_code == 200:
        responses_data = response.json()
        return responses_data['items']
    elif response.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    else:
        print(f"Ошибка получения откликов: {response.status_code}")
        return []

# Функция для отправки сообщения кандидату
async def send_message_to_candidate(messages_url, message):
    print('\n\n in send_message_to_candidate\n\n')
    url = messages_url
    headers = {'Authorization': F'Bearer {token}', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UserAgent().chrome}
    data = {
        'message': message,
    }
    response = sess.post(url, data=data, headers=headers)
    if response.status_code == 201:
        print(f"Отправка сообщения на: {messages_url}")
    elif response.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    else:
        print(f"Ошибка отправки сообщения: {response.text}")
        
async def change_state_response(url, arguments):
    print('\n\n in change_state_response\n\n')
    response = sess.put(url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UserAgent().chrome}, data=arguments)
    if response.status_code == 204:
        print(f"Смена статуса отклика успешна!")
    elif response.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    else:
        print(f"Ошибка смены статуса отклика: {response.text}\ncode: {response.status_code}")


# Получаем инфу по резюме
async def get_info_of_resume(resume_id):
    print('\n\n in get_info_of_resume\n\n')
    url = f'https://api.hh.ru/resumes/{resume_id}'
    headers = {'Authorization': F'Bearer {token}', 'Content-Type': 'application/json', 'User-Agent': UserAgent().chrome}

    response = sess.get(url, headers=headers)
    if response.status_code == 200:
        responses_data = response.json()
        return {
                'Имя': f"{responses_data['first_name']} {responses_data['middle_name']} {responses_data['last_name']}",
                'Телефон': responses_data['contact'][0]['value']['formatted'],
            }
    elif response.status_code == 403:
        refr_token(refresh_token)
        # raise ValueError('Бот был перезапущен из-за истечения срока действия токена hh.ru. Теперь должно быть все хорошо.')
    else:
        print(f"Ошибка получения инфы о резюме: {response.status_code}")
        return []
# Асинхронная функция для сбора откликов
async def collect_responses():
    print('\n\n!!!!\n\n  in collect_responses\n\n')
    while True:
        # Получаем список вакансий из базы данных
        vacancies = await get_vacancies_from_hh()
        print(f'\n\n!!!!\n\n There are {len(vacancies)} vacancies\n\n')
        # vacancies = session.query(Vacancies).all()
        list_ids_vacancies_from_db = await get_ids_vacancies()
        # Проходим по каждой вакансии
        for vacancy in vacancies:
            if vacancy['id'] in list_ids_vacancies_from_db:
                # Получаем отклики на вакансию
                responses = await get_responses_for_vacancy(vacancy['id'])

                # Проходим по каждому отклику
                for response in responses:
                    data_resume = await get_info_of_resume(response['resume']['id'])
                    if not data_resume:
                        data_resume = {
                            'Имя': f"{response['resume']['first_name']} {response['resume']['middle_name']} {response['resume']['last_name']}",
                            'Телефон': '',
                        }
                    data_candidate = {'название вакансии': vacancy['name']}
                    await create_candidate(data_resume, data_candidate)
                    id_candidate = await get_id_candidate_by_fio(data_resume.get('Имя'))
                    # Получаем ID чата кандидата
                    messages_url = response['messages_url']
                    message_for_hh_with_id = message_for_hh.replace('{title_of_vacancy}', data_candidate['название вакансии']) + str(id_candidate)
                    # Отправляем сообщение кандидату
                    await send_message_to_candidate(messages_url, message_for_hh_with_id)
                    url_resp = response['actions'][0]['url']
                    arg_resp = response['actions'][0]['arguments'][0]
                    print(f'\n\n!!!!\n\n url_resp {url_resp}\narg_resp{arg_resp}\n\n')
                    await change_state_response(url_resp, arg_resp)

        # Ждем 1 час
        await asyncio.sleep(180)


if __name__ == '__main__':
    get_token()
    # get_outh(sess)
    # asyncio.run(get_vacancies_from_hh())
    # get_vacancies(sess)
    description = '''<p>Ищем талантливого архитектора для работы над интересными проектами. </p>
<p><strong>Обязанности:</strong></p>
<ul>
  <li>Разработка концептуальных и проектных решений</li>
  <li>Подготовка проектной документации</li>
  <li>Участие в строительстве и авторском надзоре</li>
</ul>
<p><strong>Требования:</strong></p>
<ul>
  <li>Высшее архитектурное образование</li>
  <li>Опыт работы от 3 лет</li>
  <li>Знание нормативной документации</li>
  <li>Уверенное владение AutoCad, 3D Max, ArchiCad</li>
</ul>
<p><strong>Мы предлагаем:</strong></p>
<ul>
  <li>Интересные проекты</li>
  <li>Достойную заработную плату</li>
  <li>Возможность профессионального роста</li>
</ul>
<p><strong>Отправляйте резюме на [email protected]</strong></p>'''
#     description = '''Мы ищем талантливого архитектора, который присоединится к нашей команде и будет работать над интересными проектами. 

# Ваши задачи:

# * Разработка концептуальных и проектных решений
# * Подготовка проектной документации
# * Участие в строительстве и авторском надзоре

# Мы ожидаем от вас:

# * Высшее архитектурное образование
# * Опыт работы от 3 лет
# * Знание нормативной документации
# * Уверенное владение AutoCad, 3D Max, ArchiCad

# Мы предлагаем:

# * Интересные проекты
# * Достойную заработную плату
# * Возможность профессионального роста

# Отправляйте резюме на email protected'''
    # code = input('Ввод')
    # creat_vacancy(token, sess,
    #               type={'id': 'closed'},
    #               name='Архитектор',
    #               description=description,
    #               billing_type={'id': 'free'},
    #               area={"id": "6782"},
    #               professional_roles=[{"id": "123"}])

    # 
    # get_areas(sess)
    # get_professional_roles()
    # get_vacancies_from_hh()

