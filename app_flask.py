import asyncio
import logging
from aiogram import Bot, Dispatcher
from telethon import TelegramClient
from flask import Flask, jsonify, request
import threading
import time
from bot.commands import set_commands
from bot.handlers import register_handlers, check_and_notify_groups_for_birthday
from config import TELEGRAM_TOKEN, API_ID, API_HASH

# Initialize Flask app
app = Flask(__name__)

# Initialize Bot and Dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()  # Pass the bot instance to the Dispatcher

# Initialize Telethon client
telethon_client = TelegramClient('session_name', API_ID, API_HASH)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Control flag for bot task
bot_running = False


async def start_bot_with_timer(duration: int):
    """Start the bot for a specific duration."""
    global bot_running
    if bot_running:
        logging.info("Бот уже запущений.")
        return

    bot_running = True
    try:
        await set_commands(bot)
        register_handlers(dp, telethon_client)
        logging.info("Бот запущений.")

        # Run the bot for the specified duration
        await asyncio.wait_for(dp.start_polling(bot), timeout=duration)
    except asyncio.TimeoutError:
        logging.info("Час роботи бота завершено.")
    except Exception as e:
        logging.error(f"Помилка в роботі бота: {e}")
    finally:
        bot_running = False
        await stop_bot()

async def stop_bot():
    """Stop the bot."""
    global bot_running
    if not bot_running:
        logging.info("Бот вже зупинений.")
        return

    bot_running = False
    await dp.stop_polling()
    await bot.session.close()
    logging.info("Бот зупинений.")

def schedule_tasks():
    """Set up the schedule for starting and stopping the bot."""
    # while True:
    #     # asyncio.run(start_bot_with_timer(82_800))  # Запускаємо бота на 23 години
    #     asyncio.create_task(check_and_notify_groups_for_birthday())
    #     time.sleep(3_600)  # Перевіряти час кожну годину

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Установлюємо новий цикл подій
    try:
        while True:
            for i in range(2_760):
                asyncio.run(start_bot_with_timer(30))
                # Викликаємо асинхронну функцію в циклі подій
                loop.run_until_complete(check_and_notify_groups_for_birthday(bot))
            for j in range(360):
                time.sleep(10)  # Перевіряти час кожну годину
    finally:
        loop.close()  # Закриваємо цикл подій після завершення

def run_scheduler():
    """Run the schedule in a separate thread."""
    thread = threading.Thread(target=schedule_tasks)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    """Home page to show the status of the scheduler."""
    status = "Бот запущений." if bot_running else "Бот вимкнений."
    return f"Сервер Flask працює. Статус бота: {status}"


@app.route('/echo', methods=['GET'])
def echo():
    # Get all query parameters from the request
    query_params = request.args

    # Return the parameters back as a JSON response
    return jsonify({
        "echoed_data": query_params
    })

if __name__ == '__main__':
    run_scheduler()  # Start the scheduler
    app.run(port=5000, debug=False)  # Run Flask app
