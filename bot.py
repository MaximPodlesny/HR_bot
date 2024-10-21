import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start_router, search_candidate_router, handlers_router
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

# Подключение мидлвара
dp.message.middleware(LoggingMiddleware())

# Регистрация роутеров
# dp.include_router(start.router)
# dp.include_router(questionnaire.router)
# dp.include_router(handlers.router)
dp.include_router(start_router)
dp.include_router(search_candidate_router)
dp.include_router(handlers_router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

