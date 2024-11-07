from aiogram import Bot
from config import BOT_TOKEN
from collections import deque



# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)

# История чата
history = {}
