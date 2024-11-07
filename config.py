import os

from db.create_table import AdminPenal
from handlers.utils.candidate import get_db

session = get_db()

ADMINS = (session.query(AdminPenal)).admin_ids
BOT_TOKEN = os.getenv('BOT_TOKEN')
GPT_KEY = os.getenv('GPT_KEY')
DATABASE_URL = "postgresql://postgres:2565525@localhost:5432/vacancy" #"postgresql://postgres:2565525@localhost:5432/vacancy" #os.getenv('DATABASE_URL')
# print(DATABASE_URL)
ADMIN = 498283860

