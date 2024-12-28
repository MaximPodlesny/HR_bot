# from pywhatkit import sendwhatmsg_instantly
import asyncio
import requests
import json
from config import message_for_wa, API_HH, message_for_wa_by_hh


# Замените на ваши данные
api_hh = API_HH
CHAT_ID = "YOUR_CHAT_ID"

async def send_mes_whatsapp(contacts, title_of_vacancy, message_for_wa_by_hh=False):
    sess = requests.Session()
    sess.verify = False
    for contact in contacts:
        if message_for_wa_by_hh:
            message = f'{message_for_wa_by_hh.replace("{title_of_vacancy}", title_of_vacancy)}{contact[2]}'
        else:
            message = f'{message_for_wa.replace("{title_of_vacancy}", title_of_vacancy)}{contact[2]}'
        print(contact, type(contact))
        """Отправляет сообщение через Whapi.Cloud"""
        url = "https://gate.whapi.cloud/messages/text"
        headers = {
            'Authorization': f'Bearer {api_hh}',
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            "to": f"{contact[0][1:]}@s.whatsapp.net",
            # "quoted": "string",
            # "ephemeral": 0,
            # "edit": "string",
            "body": message,
            "typing_time": 0,
            "no_link_preview": True,
            # "mentions": [
            #     "string"
            # ],
            # "view_once": True
        }
        response = sess.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Сообщение успешно отправлено")
        else:
            print(f"Ошибка отправки: {response.text}")

# async def send_mes_whatsapp(contacts, message=message_for_wa):
#     for contact in contacts:
#         sendwhatmsg_instantly(phone_no=contact[0], message=message, wait_time=15, tab_close=False, close_time=30)

if __name__ == "__main__":
    asyncio.run(send_mes_whatsapp(['79898198015']))

