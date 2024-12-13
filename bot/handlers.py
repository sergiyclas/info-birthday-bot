import logging
from datetime import datetime, timedelta
from aiogram import types, Dispatcher, Bot
from aiogram.filters import Command
from functools import partial
import asyncio

from telethon import TelegramClient

from bot.utils import check_today_birthdays, get_upcoming_birthdays, get_users_dict, fetch_messages
from config import GROUP_ID, GOOGLE_SHEET_URL
user_message_count = {}

async def start_command(message: types.Message):
    logging.info(f"Команда /start отримана від користувача {message.from_user.id}")
    bot_username = (await message.bot.get_me()).username
    add_bot_link = f"https://t.me/{bot_username}?startgroup=true&admin_rights=request"
    await message.answer(f"Привіт! Додай мене до будь-якої групи за посиланням:\n{add_bot_link}")

async def top_activity_all_command(message: types.Message, telethon_client):
    logging.info(f"Команда /top_activity_all отримана від користувача {message.from_user.id}")

    # Get a dictionary of users
    users_dict = await get_users_dict(message.chat.id, message.bot)

    # Fetch messages for all time
    result_message = await fetch_messages(message, user_message_count, telethon_client, users_dict, last_n_days=None)

    if not result_message:
        await message.answer("Немає активності.")
    else:
        await message.answer(result_message, parse_mode="HTML")

async def top_activity_month_command(message: types.Message, telethon_client):
    logging.info(f"Команда /top_activity_month отримана від користувача {message.from_user.id}")

    # Get a dictionary of users
    users_dict = await get_users_dict(message.chat.id, message.bot)

    # Fetch messages for the last 30 days
    result_message = await fetch_messages(message, user_message_count, telethon_client, users_dict, last_n_days=30)

    if not result_message:
        await message.answer("Немає активності.")
    else:
        await message.answer(result_message, parse_mode="HTML")


async def top_activity_day_command(message: types.Message, telethon_client):
    logging.info(f"Команда /top_activity_day отримана від користувача {message.from_user.id}")

    # Get a dictionary of users
    users_dict = await get_users_dict(message.chat.id, message.bot)
    # print(users_dict)
    # Fetch messages for the last 30 days
    result_message = await fetch_messages(message, user_message_count, telethon_client, users_dict, last_n_days=1)

    if not result_message:
        await message.answer("Немає активності.")
    else:
        await message.answer(result_message, parse_mode="HTML")


async def cmd_check_today_birthdays(message: types.Message):
    result_message = await check_today_birthdays(GOOGLE_SHEET_URL, message)
    await message.reply(result_message)

async def cmd_upcoming_birthdays(message: types.Message):
    result_message = await get_upcoming_birthdays(GOOGLE_SHEET_URL)
    # print(message.chat.id)
    await message.reply(result_message)

async def check_and_notify_groups_for_birthday(bot):
    # print('RUUUUUUUUUN')
    """Функція для перевірки та надсилання повідомлень у групи."""
    messages = await check_today_birthdays(GOOGLE_SHEET_URL)
    if messages:
        text = "\n".join(messages)
        if GROUP_ID:
            try:
                await bot.send_message(GROUP_ID, text)
                await asyncio.sleep(1)  # Затримка для уникнення ліміту
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення до групи {GROUP_ID}: {e}")
    # await bot.send_message(GROUP_ID, 'Everything works')

def register_handlers(dp: Dispatcher, telethon_client: TelegramClient):
    dp.message.register(start_command, Command(commands=['start']))
    dp.message.register(partial(top_activity_all_command, telethon_client=telethon_client),
                        Command(commands=['top_activity_all']))
    dp.message.register(partial(top_activity_month_command, telethon_client=telethon_client),
                        Command(commands=['top_activity_month']))
    dp.message.register(cmd_check_today_birthdays, Command(commands=['today_birthdays']))
    dp.message.register(cmd_upcoming_birthdays, Command(commands=['upcoming_birthdays']))
    dp.message.register(partial(top_activity_day_command, telethon_client=telethon_client),
                        Command(commands=['top_activity_day']))
