from .candidate import create_candidate
from aiogram import Router, types

router = Router()
def search_c():
    create_candidate()