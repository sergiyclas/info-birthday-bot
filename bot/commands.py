from aiogram import Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Почати роботу з ботом"),
        BotCommand(command="/top_activity_all", description="Показати топ активних користувачів за весь час"),
        BotCommand(command="/top_activity_month", description="Показати топ активних користувачів за останні 30 днів"),
        BotCommand(command="/top_activity_day", description="Показати топ активних користувачів за останній день"),
        BotCommand(command="/today_birthdays", description="Перевірити чи хтось сьогодні святкує день народження"),
        BotCommand(command="/upcoming_birthdays", description="Показати 5 найближчих днів народжень"),

    ]
    await bot.set_my_commands(commands)
