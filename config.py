import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot and Telegram client configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
GROUP_ID = os.getenv('GROUP_ID')
GOOGLE_SHEET_URL = os.getenv('GOOGLE_SHEET_URL')