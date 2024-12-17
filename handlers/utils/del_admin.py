import asyncio
import os
import subprocess
import sys

import psutil
# from asyncio import subprocess
from db.create_table import AdminPenal
# from bot import bot
# from main import dp
from handlers.utils.admins import g_a
from handlers.utils.candidate import get_db
from handlers.utils.get_admin_ids import get_admins


async def del_admin_id(id):
    session = get_db()
    admins = session.query(AdminPenal).first()
    admins.admin_ids = ' '.join([i for i in admins.admin_ids.split(' ') if i != str(id)])

    session.add(admins)
    session.commit()
    # Получаем PID текущего процесса
    current_pid = os.getpid()
    # asyncio.run(dp.stop_polling())
    # os._exit(20)
    # await asyncio.sleep(20)
    # await bot.close()  # Закрываем текущее соединение бота
    # await asyncio.sleep(10)  # Пауза для завершения работы
    subprocess.run([r'I:\Projects Python\HR_bot\venv\Scripts\python', 'main.py']) 
    # subprocess.run(["python", "main.py"]) 
    # Находим процесс по PID
    process = psutil.Process(current_pid)

    # Завершаем процесс
    process.terminate()