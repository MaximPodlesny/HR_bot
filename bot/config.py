import os

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# HH.ru API Key
HH_API_KEY = os.getenv("HH_API_KEY")

# Bitrix24 API Key
BITRIX_API_KEY = os.getenv("BITRIX_API_KEY")

# Bitrix24 Domain
BITRIX_DOMAIN = os.getenv("BITRIX_DOMAIN")

# Bitrix24 API URL
BITRIX_API_URL = f"https://{BITRIX_DOMAIN}.bitrix24.com/rest"

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# ... (Other configuration settings if needed)

# Check if all required environment variables are set
if not all([
    TELEGRAM_BOT_TOKEN,
    OPENAI_API_KEY,
    HH_API_KEY,
    BITRIX_API_KEY,
    BITRIX_DOMAIN,
    DATABASE_URL,
]):
    raise ValueError("Missing environment variables. Please set them in your environment.")