# Бот для проверки статуса домашки на DVMN

Лонгпулит dvmn на изменения в статусе проверки домашки.
Отчитывается и пишет логи в телеграм.

## Setup
Возможно использовать как локально, так и на Heroku
### Local
1. Создать `.env` файл
### Heroku
1. Создать app на [heroku](https://www.heroku.com/) и добавить переменные в Settings -> Config Vars

## Env
Необходимы следующие переменные окружения:
- DVMN_TOKEN - str, токен на DVMN
- BOT_TOKEN - str, токен от [BotFather](https://t.me/botfather)
- BOT_REPORTER_TOKEN - Optional[str], токен для бота для логирования
- CHAT_ID - str, id пользователя в телеграм

## Local Start
```
python main.py
```
