import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from bot import bot
from handlers import start_router, search_candidate_router, handlers_admin_router, search_candidate_by_data_router, handlers_for_candidates_router, questionnaire_router
from handlers.utils.chat_history import ChatHistory
from middlewares.logging import LoggingMiddleware
from db.create_table import create_tables
from config import BOT_TOKEN


# Настройка логирования
logging.basicConfig(level=logging.INFO)

create_tables()

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
dp.include_router(handlers_admin_router)
dp.include_router(search_candidate_by_data_router)
dp.include_router(handlers_for_candidates_router)
dp.include_router(questionnaire_router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

