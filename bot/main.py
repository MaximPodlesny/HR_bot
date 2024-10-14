import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.handlers import setup

from bot.config import TELEGRAM_BOT_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Register handlers
setup(dp)

if __name__ == "__main__":
    asyncio.run(executor.start_polling(dp, skip_updates=True))