import requests
import pandas as pd
from collections import defaultdict

from dateutil.utils import today
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from datetime import datetime, timedelta

from config import TELEGRAM_TOKEN

# Store the number of messages for each user
user_message_count = defaultdict(int)

async def get_users_dict(chat_id, bot):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChatAdministrators'
    response = requests.get(url, params={'chat_id': chat_id})
    data = response.json()

    users_dict = {}
    if data['ok']:
        for admin in data['result']:
            user = admin['user']
            users_dict[user['id']] = user['username'] or user['first_name']
    else:
        users_dict[0] = None
    return users_dict


async def fetch_messages(message, user_message_count, client, users_dict, last_n_days=None):
    async with client:
        chat_id = message.chat.id
        peer = PeerChannel(chat_id)

        # Initialize offset and limit
        offset_id = 0
        limit = 100  # Batch size
        total_messages_fetched = 0
        thirty_days_ago = datetime.now().astimezone() - timedelta(days=last_n_days) if last_n_days else None

        user_message_count.clear()

        while True:
            history = await client(GetHistoryRequest(
                peer,
                limit=limit,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            for msg in history.messages:
                # print(msg)
                if last_n_days is None or (msg.date and msg.date >= thirty_days_ago):
                    if msg.from_id:
                        user_id = msg.from_id.user_id if hasattr(msg.from_id, 'user_id') else msg.from_id

                        if user_id not in user_message_count:
                            user_message_count[user_id] = 0

                        user_message_count[user_id] += 1

            offset_id = history.messages[-1].id
            total_messages_fetched += len(history.messages)

            if len(history.messages) < limit:
                break

    # Sort users by message count over the last 30 days
    sorted_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)

    if not sorted_users:
        return

    # Build the result message
    result_message = f"<b>Топ активних учасників за останні {last_n_days} днів:</b>\n" if last_n_days is not None else  "<b>Топ активних учасників за весь час:</b>\n"
    for i, (user_id, count) in enumerate(sorted_users, 1):
        result_message += f"{i}. {users_dict.get(user_id, 'Indefiend')} - {count} повідомлень\n"

    return result_message


async def fetch_birthdays_from_csv(csv_url):
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        return f'Smth went wrong during downloading birthdays: {e}'
    # print(df)
    return df


async def get_sorted_birthdays(df):

    birthday_dict = {}
    for index, i in enumerate(df['Unnamed: 5']):
        if str(i)[6:9] == '200':
            # print(df['Unnamed: 4'][index], df['Unnamed: 5'][index]) # nickname, date
            birthday_dict[df['Unnamed: 5'][index]] = df['Unnamed: 4'][index]

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Створюємо новий список, який включатиме поточний рік для порівняння
    sorted_birthdays = []
    for date_str, username in birthday_dict.items():
        birthday_date = datetime.strptime(date_str, '%d.%m.%Y')

        # Змінюємо рік на поточний для точного порівняння
        adjusted_birthday = birthday_date.replace(year=today.year)

        # Якщо день народження вже минув цього року, переносимо його на наступний рік
        # print(adjusted_birthday, yesterday, today)
        if adjusted_birthday < yesterday:
            adjusted_birthday = adjusted_birthday.replace(year=today.year + 1)

        sorted_birthdays.append((adjusted_birthday, username))

    sorted_birthdays.sort(key=lambda x: x[0])
    # print(sorted_birthdays)
    return sorted_birthdays


async def check_today_birthdays(csv_url, mess=None):
    df = await fetch_birthdays_from_csv(csv_url)
    sorted_birthdays = await get_sorted_birthdays(df)

    # print(sorted_birthdays)
    # print(df)
    today = datetime.now().date()  # Отримуємо сьогоднішню дату у форматі datetime.date()
    # today = '2024-11-02'
    # print(today)

    messages = []
    for date_member, nick in sorted_birthdays:
        # Порівнюємо тільки дати без часу
        # print(date.date(), today)
        if date_member.date() == today:
            messages.append(f"Вітаю з днем народження! {nick}")

    if mess and not messages:
        return "Сьогодні немає днів народження."
    elif not mess and not messages:
        return ""

    return "\n".join(messages)


async def get_upcoming_birthdays(csv_url, limit=5):
    df = await fetch_birthdays_from_csv(csv_url)
    sorted_birthdays = await get_sorted_birthdays(df)

    if not sorted_birthdays:
        return "Немає найближчих днів народження."

    if limit < 1:
        limit = 1

    today = datetime.now().date()  # Отримуємо поточну дату
    messages = []

    for index, (date, nick) in enumerate(sorted_birthdays):
        days_left = (date.date() - today).days  # Обчислюємо різницю в днях
        formatted_date = date.strftime('%d.%m.%Y')  # Форматування дати
        messages.append(f"{index + 1}. {formatted_date} - {nick} ({days_left} днів залишилось)")

        if index >= limit - 1:
            break

    return "\n".join(messages)
