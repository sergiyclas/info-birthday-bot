import pandas as pd
from datetime import datetime, timedelta

from urllib3 import proxy_from_url


# Зчитуємо дані з таблиці
def fetch_birthdays_from_csv(csv_url):
    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        return f'Smth went wrong during downloading birthdays: {e}'
    # print(df)
    return df

# Функція для підготовки даних і сортування днів народжень
def get_sorted_birthdays(df):

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
        print(adjusted_birthday, yesterday, today)
        print('what')
        if adjusted_birthday < yesterday:
            adjusted_birthday = adjusted_birthday.replace(year=today.year + 1)

        sorted_birthdays.append((adjusted_birthday, username))

    sorted_birthdays.sort(key=lambda x: x[0])
    # print(sorted_birthdays)
    return sorted_birthdays

# Виводимо найближчі дні народження
def get_upcoming_birthdays(csv_url, limit=5):
    df = fetch_birthdays_from_csv(csv_url)
    sorted_birthdays = get_sorted_birthdays(df)

    if not sorted_birthdays:
        return "Немає найближчих днів народження."

    if limit < 1:
        limit = 1
    messages = []
    for index, (date, nick) in enumerate(sorted_birthdays):
        messages.append(f"{index}. {date} - {nick}")
        if index >= limit - 1:
            break
    return "\n".join(messages)

# Перевіряємо дні народження сьогодні
def check_today_birthdays(csv_url):
    df = fetch_birthdays_from_csv(csv_url)
    sorted_birthdays = get_sorted_birthdays(df)

    today = datetime.now().date()  # Отримуємо сьогоднішню дату у форматі datetime.date()
    # today = '2024-11-02'

    messages = []
    for date, nick in sorted_birthdays:
        # Порівнюємо тільки дати без часу
        # print(date.date(), today)
        if date.date() == today:
            messages.append(f"Вітаю з днем народження! {nick}")

    if not messages:
        return "Сьогодні немає днів народження."

    return "\n".join(messages)


# URL до Google Sheets у форматі CSV
from config import GOOGLE_SHEET_URL

# Зчитуємо дані та виводимо результати
df = fetch_birthdays_from_csv(GOOGLE_SHEET_URL)
print(get_upcoming_birthdays(GOOGLE_SHEET_URL))
print(check_today_birthdays(GOOGLE_SHEET_URL))
