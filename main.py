import logging
import os
from time import sleep

import requests
import telegram
from environs import Env


class MyLogsHandler(logging.Handler):
    def __init__(self, tg_token: str, chat_id: str):
        super().__init__()
        self.token = tg_token
        self.chat_id = chat_id

    def emit(self, record):
        log_bot = telegram.Bot(token=BOT_TOKEN)
        log_bot.send_message(self.chat_id, self.format(record))


def get_logger(bot_reporter_token, chat_id):
    logger = logging.getLogger("homework")
    logger.setLevel(logging.DEBUG)

    strfmt = "[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

    handler_st = logging.StreamHandler()
    handler_st.setFormatter(formatter)

    if bot_reporter_token and chat_id:
        strfmt = "%(asctime)s :: %(levelname)s :: %(message)s"
        datefmt = "%d.%m %H:%M:%S"
        formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

        handler_tg = MyLogsHandler(bot_reporter_token, chat_id)
        handler_tg.setFormatter(formatter)

        logger.addHandler(handler_st)
        logger.addHandler(handler_tg)

    return logger


def say_hello(bot, chat_id):
    bot.send_message(chat_id=chat_id, text=f"I'm ready!")
    logger.info(f"Bot '{bot.name}' is started")


def attempt_checker(dvmn_token, bot, chat_id):
    headers = {"Authorization": f"Token {dvmn_token}"}
    url = "https://dvmn.org/api/long_polling/"
    time_stamp = None

    while True:
        params = {"time_stamp": time_stamp}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=90)
            response.raise_for_status()
            attempts = response.json()
            if attempts["status"] == "found":
                time_stamp = attempts["last_attempt_timestamp"]
                for attempt in attempts["new_attempts"]:
                    msg = f'Преподаватель проверил работу "{attempt["lesson_title"]}"!\n\n'
                    if attempt["is_negative"]:
                        msg += "Придется поработать!\n"
                        msg += f'{attempt["lesson_url"]}'
                    else:
                        msg += "Наконец ты справился!"
                    bot.send_message(chat_id=chat_id, text=msg)
            else:
                time_stamp = attempts["timestamp_to_request"]
        except requests.exceptions.ConnectionError:
            logger.info("Test connection...")
            sleep(3)
        except requests.exceptions.Timeout:
            pass
        except ZeroDivisionError as e:
            logger.exception("division by zero")
            sleep(3)


if __name__ == "__main__":
    env = Env()
    env.read_env()

    DVMN_TOKEN = os.environ["DVMN_TOKEN"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    BOT_REPORTER_TOKEN = os.getenv("BOT_REPORTER_TOKEN", BOT_TOKEN)
    CHAT_ID = os.environ["CHAT_ID"]

    logger = get_logger(bot_reporter_token=BOT_REPORTER_TOKEN, chat_id=CHAT_ID)

    bot = telegram.Bot(token=BOT_TOKEN)

    say_hello(bot, CHAT_ID)
    attempt_checker(DVMN_TOKEN, bot, CHAT_ID)
