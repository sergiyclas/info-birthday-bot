import requests

# Введіть ваш API токен та ID чату

url = f'https://api.telegram.org/bot{api_token}/getChatAdministrators'

response = requests.get(url, params={'chat_id': chat_id})
data = response.json()

users_dict = {}

if data['ok']:
    for admin in data['result']:
        user = admin['user']
        print(user['username'] or user['first_name'], user['id'])
        users_dict[user['id']] = user['username'] or user['first_name']
else:
    print('Error:', data['description'])
