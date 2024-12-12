import asyncio
import logging
from aiogram import Bot, Dispatcher
from telethon import TelegramClient

from bot.commands import set_commands
from bot.handlers import register_handlers
from config import TELEGRAM_TOKEN, API_ID, API_HASH

# Initialize Bot and Dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()  # Pass the bot instance to the Dispatcher

# Initialize Telethon client
telethon_client = TelegramClient('session_name', API_ID, API_HASH)

# Logging configuration
logging.basicConfig(level=logging.INFO)

async def main():
    await set_commands(bot)  # Set bot commands
    register_handlers(dp, telethon_client)  # Pass the Telethon client to handlers

    logging.info("Бот успішно запущений та очікує команди...")
    await dp.start_polling(bot)  # Start polling the bot

if __name__ == '__main__':
    asyncio.run(main())


"""
{7190145957: 'chat_nfo_bot', 1825726930: 'andriyhavryliv', 1730544367: 'khristina_jaciruk', 1596405429: 'V_Vitaliiy', 1329615264: 'romannsss', 1081325110: 'vctrstrk', 751853129: 'mexicancat228', 675623809: 'deansand'}
"""