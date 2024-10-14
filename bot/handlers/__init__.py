from aiogram import Dispatcher
from bot.handlers import start, vacancy, candidate, admin

def setup(dp: Dispatcher):
    start.setup(dp)
    vacancy.setup(dp)
    candidate.setup(dp)
    admin.setup(dp)