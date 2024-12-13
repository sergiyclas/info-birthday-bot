import asyncio
import logging
from aiogram import Bot, Dispatcher
from telethon import TelegramClient
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from bot.commands import set_commands
from bot.handlers import register_handlers, check_and_notify_groups_for_birthday
from config import TELEGRAM_TOKEN, API_ID, API_HASH
from aiogram.fsm.storage.memory import MemoryStorage
from pytz import timezone

kyiv_tz = timezone("Europe/Kyiv")

# Initialize Flask app
app = Flask(__name__)

# Initialize Bot
bot = Bot(token=TELEGRAM_TOKEN)

# Initialize Dispatcher with in-memory storage
dp = Dispatcher(storage=MemoryStorage())

# Initialize Telethon client
telethon_client = TelegramClient('session_name', API_ID, API_HASH)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Scheduler for periodic tasks
scheduler = BackgroundScheduler()

@app.route('/')
def index():
    """Home page to show the status of the bot."""
    status = "Бот запущений." if scheduler.running else "Бот вимкнений."
    return f"Сервер Flask працює. Статус бота: {status}"


@app.route('/echo', methods=['GET'])
def echo():
    # Get all query parameters from the request
    query_params = request.args

    # Return the parameters back as a JSON response
    return jsonify({
        "echoed_data": query_params
    })


async def start_bot():
    """Start the bot."""
    await set_commands(bot)
    register_handlers(dp, telethon_client)
    logging.info("Бот запущений.")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()  # Закриваємо сесію бота
        await dp.shutdown()       # Закриваємо Dispatcher


def start_bot_task():
    """Function to run bot in the main event loop."""
    asyncio.run(start_bot())


def run_scheduler():
    """Run the schedule in a separate thread."""
    scheduler.add_job(
        lambda: asyncio.run(check_and_notify_groups_for_birthday(bot)),
        'cron',
        hour=8,
        minute=1,
        timezone=kyiv_tz
    )
    scheduler.start()

    # Запускаємо бота прямо тут
    start_bot_task()


if __name__ == '__main__':
    run_scheduler()  # Start the scheduler
    app.run(debug=False)  # Run Flask app
