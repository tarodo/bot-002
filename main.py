import os
from time import sleep

import requests
import telegram
from environs import Env

env = Env()
env.read_env()

DVMN_TOKEN = os.environ["DVMN_TOKEN"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = telegram.Bot(token=BOT_TOKEN)
chat = bot.get_chat(CHAT_ID)

bot.send_message(text=f'Hello, {chat.first_name}!', chat_id=CHAT_ID)

headers = {'Authorization': f'Token {DVMN_TOKEN}'}
url = 'https://dvmn.org/api/long_polling/'
time_stamp = None

while True:
    params = {'time_stamp': time_stamp}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=90)
        response.raise_for_status()
        attempts = response.json()
        if attempts['status'] == 'found':
            time_stamp = attempts['last_attempt_timestamp']
            for attempt in attempts['new_attempts']:
                msg = f'Преподаватель проверил работу "{attempt["lesson_title"]}"!\n\n'
                if attempt['is_negative']:
                    msg += 'Придется поработать!\n'
                    msg += f'{attempt["lesson_url"]}'
                else:
                    msg += 'Наконец ты справился!'
                bot.send_message(chat_id=CHAT_ID, text=msg)
        else:
            time_stamp = attempts['timestamp_to_request']
    except requests.exceptions.ConnectionError:
        print('Test connection...')
        sleep(3)
    except requests.exceptions.Timeout:
        pass