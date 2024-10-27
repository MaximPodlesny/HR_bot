import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from handlers import start_router, search_candidate_router, handlers_router, search_candidate_by_data_router
from handlers.utils.chat_history import ChatHistory
from middlewares.logging import LoggingMiddleware
from db.create_table import create_tables
from config import BOT_TOKEN


# Настройка логирования
logging.basicConfig(level=logging.INFO)

create_tables()
# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

ChatHistory
# Подключение мидлвара
dp.message.middleware(LoggingMiddleware())

# Регистрация роутеров
# dp.include_router(start.router)
# dp.include_router(questionnaire.router)
# dp.include_router(handlers.router)
dp.include_router(start_router)
dp.include_router(search_candidate_router)
dp.include_router(handlers_router)
dp.include_router(search_candidate_by_data_router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

