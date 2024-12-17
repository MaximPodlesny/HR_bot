import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
GPT_KEY = os.getenv('GPT_KEY')
API_HH = os.getenv('API_HH')
DATABASE_URL = os.getenv('DATABASE_URL')

ADMIN = 498283860
message_for_hh = "Здравствуйте! Спасибо за ваш отклик на вакансию {title_of_vacancy}. Ваша кандидатура показалась нам очень интересной, приглашаем Вас пройти предварительное собеседование в телеграм: https://t.me/hackatoshik_bot?start="
message_for_wa = "Здравствуйте! Спасибо за ваш отклик на вакансию {title_of_vacancy}. Ваша кандидатура показалась нам очень интересной, приглашаем Вас пройти предварительное собеседование в телеграм: https://t.me/hackatoshik_bot?start="

