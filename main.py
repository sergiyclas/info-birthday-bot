import asyncio
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.enums import ParseMode
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

# Завантажуємо змінні середовища з файлу .env
load_dotenv()

# Токен від BotFather
TOKEN = os.getenv('TELEGRAM_TOKEN')
API_ID = os.getenv('API_ID')  # https://my.telegram.org/apps
API_HASH = os.getenv('API_HASH')  # https://my.telegram.org/apps
GROUP_NAME = os.getenv('GROUP_NAME')

# Ініціалізація бота і диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ініціалізація Telegram клієнта
client = TelegramClient('session_name', int(API_ID), API_HASH)

# Встановлення рівня логування
logging.basicConfig(level=logging.INFO)

# Зберігаємо кількість повідомлень кожного користувача
user_message_count = defaultdict(int)

async def get_users_dict(GROUP_NAME):
    url = f'https://api.telegram.org/bot{TOKEN}/getChatAdministrators'

    response = requests.get(url, params={'chat_id': GROUP_NAME})
    data = response.json()

    users_dict = {}

    if data['ok']:
        for admin in data['result']:
            user = admin['user']
            users_dict[user['id']] = user['username'] or user['first_name']
    else:
        users_dict[0] = None
    return users_dict

# Команда /start
@dp.message(Command(commands=['start']))
async def start_command(message: types.Message):
    if message.chat.type in ["private"]:
        logging.info(f"Команда /start отримана від користувача {message.from_user.id}")

        bot_username = (await bot.get_me()).username
        add_bot_link = f"https://t.me/{bot_username}?startgroup=true&admin_rights=request"

        await message.answer(
            f"Привіт! Додай мене до будь-якої групи за посиланням нижче та надай мені права адміністратора:\n{add_bot_link}"
        )
    return

@dp.message(Command(commands=['top_activity_all']))
async def top_activity_all_command(message: types.Message):
    logging.info(f"Команда /top_activity_all отримана від користувача {message.from_user.id}")

    users_dict = await get_users_dict(GROUP_NAME)

    if message.chat.type in ["group", "supergroup"]:
        async with client:
            chat_id = message.chat.id
            peer = PeerChannel(chat_id)

            # Initialize offset_id and batch size
            offset_id = 0
            limit = 100  # Batch size
            total_messages_fetched = 0  # Track the total number of fetched messages

            # Clear the message count before starting
            user_message_count.clear()

            while True:
                # Fetch the next batch of messages
                history = await client(GetHistoryRequest(
                    peer,
                    limit=limit,  # Number of messages to retrieve per batch
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))

                if not history.messages:
                    # Break the loop if no more messages are returned
                    break

                # Process each message in the batch
                for msg in history.messages:
                    if msg.from_id:
                        user_id = msg.from_id.user_id if hasattr(msg.from_id, 'user_id') else msg.from_id
                        user_message_count[user_id] += 1

                # Update the offset_id to fetch the next batch of messages
                offset_id = history.messages[-1].id

                # Track the total messages fetched (optional logging)
                total_messages_fetched += len(history.messages)
                logging.info(f"Fetched {total_messages_fetched} messages so far...")

                # Stop if no more messages are available
                if len(history.messages) < limit:
                    break

    # Sort users by message count (all time)
    sorted_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)

    if not sorted_users:
        logging.info("Немає активності")
        await message.answer("Немає активності.")
        return

    # Build the result message
    result_message = "<b>Топ активних учасників за весь час:</b>\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        result_message += f"{i}. @{users_dict.get(user_id, 'Indefiend')} - {count} повідомлень\n"
        logging.info(f"{i}. {user_id} @{users_dict.get(user_id, 'Indefiend')} - {count} повідомлень")

    await message.answer(result_message, parse_mode=ParseMode.HTML)
    logging.info("Відповідь на команду /top_activity_all надіслана.")


@dp.message(Command(commands=['top_activity_month']))
async def top_activity_month_command(message: types.Message):
    logging.info(f"Команда /top_activity_month отримана від користувача {message.from_user.id}")

    users_dict = await get_users_dict(GROUP_NAME)

    if message.chat.type in ["group", "supergroup"]:
        async with client:
            chat_id = message.chat.id
            peer = PeerChannel(chat_id)

            # Make thirty_days_ago timezone-aware
            thirty_days_ago = datetime.now().astimezone() - timedelta(days=30)

            # Initialize offset_id and batch size
            offset_id = 0
            limit = 100  # Batch size
            total_messages_fetched = 0  # Track the total number of fetched messages

            # Clear the message count before starting
            user_message_count.clear()

            while True:
                # Fetch the next batch of messages
                history = await client(GetHistoryRequest(
                    peer,
                    limit=limit,  # Number of messages to retrieve per batch
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))

                if not history.messages:
                    # Break the loop if no more messages are returned
                    break

                # Process each message in the batch
                for msg in history.messages:
                    if msg.date and msg.date >= thirty_days_ago:
                        if msg.from_id:
                            user_id = msg.from_id.user_id if hasattr(msg.from_id, 'user_id') else msg.from_id
                            user_message_count[user_id] += 1

                # Update the offset_id to fetch the next batch of messages
                offset_id = history.messages[-1].id

                # Track the total messages fetched (optional logging)
                total_messages_fetched += len(history.messages)
                logging.info(f"Fetched {total_messages_fetched} messages so far...")

                # Stop if no more messages are available
                if len(history.messages) < limit:
                    break

    # Sort users by message count over the last 30 days
    sorted_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)

    if not sorted_users:
        logging.info("Немає активності за останні 30 днів")
        await message.answer("Немає активності за останні 30 днів.")
        return

    # Build the result message
    result_message = "<b>Топ активних учасників за останні 30 днів:</b>\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        result_message += f"{i}. @{users_dict.get(user_id, 'Indefiend')} - {count} повідомлень\n"
        logging.info(f"{i}. {user_id} @{users_dict.get(user_id, 'Indefiend')} - {count} повідомлень")

    await message.answer(result_message, parse_mode=ParseMode.HTML)
    logging.info("Відповідь на команду /top_activity_month надіслана.")


# Обробляємо кількість повідомлень користувачів
@dp.message()
async def count_messages(message: types.Message):
    logging.info(f"Отримано повідомлення від користувача {message.from_user.id} в чаті {message.chat.id}")

    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id
        user_message_count[user_id] += 1
        logging.info(f"Збільшено кількість повідомлень користувача {user_id} до {user_message_count[user_id]}")

# Основна функція для запуску бота
async def main():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Почати роботу з ботом"),
        BotCommand(command="/top_activity_all", description="Показати топ активних користувачів за весь час"),
        BotCommand(command="/top_activity_month", description="Показати топ активних користувачів за останні 30 днів")
    ])

    logging.info("Бот успішно запущений та очікує команди...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
