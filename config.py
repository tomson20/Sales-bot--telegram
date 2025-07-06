import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
#STRIPE_PROVIDER_TOKEN = os.getenv("STRIPE_PROVIDER_TOKEN")