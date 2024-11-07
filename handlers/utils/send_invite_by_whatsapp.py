from pywhatkit import sendwhatmsg_instantly

async def send_mes_whatsapp(contacts, message='Приглашение'):
    for contact in contacts:
        sendwhatmsg_instantly(phone_no=contact[0], message=message, wait_time=15, tab_close=False, close_time=30)