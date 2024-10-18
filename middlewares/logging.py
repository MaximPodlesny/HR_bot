import logging
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Update

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logging.info(f'Update: {event}')
        return await handler(event, data)
