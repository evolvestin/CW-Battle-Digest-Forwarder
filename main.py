import os
import re
import asyncio
import _thread
import gspread
import functions
from SQL import SQL
from time import sleep
from aiogram import types
from copy import copy, deepcopy
from aiogram.utils import executor
from string import ascii_uppercase
from aiogram.dispatcher import Dispatcher
from datetime import datetime, timezone, timedelta
from functions import bold, italic, stamper, time_now
# =================================================================================================================
stamp1 = time_now()


def users_db_creation():
    db = SQL(db_path)
    spreadsheet = gspread.service_account('forwarding.json').open('UNITED USERS')
    users = spreadsheet.worksheet(os.environ['sheet']).get('A1:Z50000', major_dimension='ROWS')
    raw_columns = db.create_table('users', users.pop(0), additional=True)
    users_ids, columns = db.upload('users', raw_columns, users)
    _zero_user = db.get_user(0)
    db.close()
    return _zero_user, ['id', *users_ids], columns


db_path = 'db/database.db'
Auth = functions.AuthCentre(LOG_DELAY=120,
                            ID_DEV=-1001312302092,
                            TOKEN=os.environ.get('TOKEN'),
                            ID_DUMP=os.environ.get('ID_DUMP'),
                            ID_LOGS=os.environ.get('ID_LOGS'),
                            ID_MEDIA=os.environ.get('ID_MEDIA'),
                            DEV_TOKEN=os.environ.get('DEV_TOKEN'),
                            ID_FORWARD=os.environ.get('ID_FORWARD'))

bot, dispatcher = Auth.async_bot, Dispatcher(Auth.async_bot)
functions.environmental_files(), os.makedirs('db', exist_ok=True)
zero_user, google_users_ids, users_columns = users_db_creation()
tz, logging, start_message = timezone(timedelta(hours=3)), [], None
channels = [os.environ.get(key) for key in ['ID_DUMP', 'ID_MEDIA', 'ID_FORWARD', 'ID_DIGEST_RU', 'ID_DIGEST_EN']]
channels.extend([*os.environ.get('ID_LOGS').split(' '), str(Auth.dev.chat_id)])
# =================================================================================================================


def lang_text(lang: str):
    return f"✅ Lang: {bold(lang.upper())} (GMT+{0 if lang == 'en' else 3}). Change: /lang"


def first_start(message):
    db, user = SQL(db_path), deepcopy(zero_user)
    _, name, username = Auth.logs.header(message['chat'].to_python())
    user.update({
        'name': name,
        'username': username,
        'id': message['chat']['id']})
    db.create_user(user)
    db.close()
    return lang_text(user['lang'])


def chats_to_human(count, seconds):
    text = f'В {count} чат'
    if str(count)[-2:] in ['11', '12', '13', '14']:
        text += 'ов'
    elif str(count)[-1] != '1':
        text += 'а' if str(count)[-1] in ['2', '3', '4'] else 'ов'

    if 0 < seconds < 1:
        text += f" за {f'{seconds}0' if len(str(seconds)) == 3 else seconds} секунды"
    else:
        seconds = int(seconds)
        text += f' за {seconds} секунд'
        if seconds < 10 or seconds > 20:
            text += 'у' if str(seconds)[-1] in ['1'] else ''
            text += 'ы' if str(seconds)[-1] in ['2', '3', '4'] else ''
    return f'{text}.'


async def sender(message, user, text=None, log_text=None, **a_kwargs):
    global logging
    task = a_kwargs.get('func') or bot.send_message
    dump = True if 'Впервые' in str(log_text) else None
    kwargs = {'log': log_text, 'text': text, 'user': user, 'message': message, **a_kwargs}
    response, log_text, update = await Auth.async_message(task, **kwargs)
    if log_text is not None:
        logging.append(log_text)
        if dump:
            head, _, _ = Auth.logs.header(Auth.get_me)
            await Auth.async_message(bot.send_message, id=Auth.logs.dump_chat_id, text=f'{head}{log_text}')
    if update:
        db = SQL(db_path)
        db.update('users', user['id'], update)
        db.close()
    return response


@dispatcher.chat_member_handler()
@dispatcher.my_chat_member_handler()
async def member_handler(message: types.ChatMember):
    global logging
    try:
        if str(message['chat']['id']) not in channels:
            db = SQL(db_path)
            text, user = None, db.get_user(message['chat']['id'])
            log_text, update, greeting = Auth.logs.chat_member(message, db.get_user(message['chat']['id']))
            if greeting:
                text = 'Добро пожаловать, снова'
                if user is None:
                    await asyncio.sleep(1)
                    text = first_start(message)
            logging.append(log_text)
            db.update('users', message['chat']['id'], update) if update else None
            await Auth.async_message(bot.send_message, id=message['chat']['id'], text=text)
            db.close()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


@dispatcher.channel_post_handler()
async def repeat_channel_messages(message: types.Message):
    global start_message
    try:
        if str(message['chat']['id']) in [os.environ['ID_DIGEST_RU'], os.environ['ID_DIGEST_EN']]:
            lang = 'en' if str(message['chat']['id']) == os.environ['ID_DIGEST_EN'] else 'ru'
            battle, search = None, re.search(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})', message['text'])
            if search:
                battle_stamp = stamper(search.group(1), delta=0 if lang == 'en' else 3, pattern='%d/%m/%Y %H:%M')
                condition = (time_now() - battle_stamp) < 1800 and (time_now() - dict(message).get('date')) < 1800
                if condition or os.environ.get('local'):
                    battle = Auth.time(battle_stamp, form='normal', sep='/', tag=italic, seconds=None)

            if battle:
                db = SQL(db_path)
                users = db.get_users(lang)
                stamp = datetime.now(tz).timestamp()
                db.close()
                coroutines = [sender(message, user=user, func=bot.forward_message, id=user['id']) for user in users]
                await asyncio.gather(*coroutines)
                text = bold(chats_to_human(len(users), round(datetime.now(tz).timestamp() - stamp, 3)))
                start_message = Auth.message(
                    old_message=start_message, text=f"\n\nСводки {bold(lang.upper())} {battle}:\n{text}")
        else:
            if str(message['chat']['id']) not in channels:
                db = SQL(db_path)
                text, log_text = None, None
                user = db.get_user(message['chat']['id'])
                if user is None:
                    text, log_text = first_start(message), ' [#Впервые]'
                await sender(message, user=user, text=text, log_text=log_text)
                db.close()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


@dispatcher.message_handler(content_types=functions.red_contents)
async def red_messages(message: types.Message):
    try:
        db = SQL(db_path)
        text, user = None, db.get_user(message['chat']['id'])
        if user and message['migrate_to_chat_id']:
            db.update('users', user['id'], {'username': 'DISABLED_GROUP', 'reaction': '🅾️'})
        await sender(message, user, text=text, log_text=True)
        db.close()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


@dispatcher.message_handler()
async def repeat_all_messages(message: types.Message):
    try:
        db = SQL(db_path)
        user = db.get_user(message['chat']['id'])
        text, log_text = None, True
        if user:
            if message['text'].lower().startswith('/reg'):
                text = lang_text(user['lang'])

            elif message['text'].lower().startswith('/lang'):
                text = lang_text('ru' if user['lang'] == 'en' else 'en')
                db.update('users', user['id'], {'lang': 'ru' if user['lang'] == 'en' else 'en'})

            elif str(message['chat']['id']) in os.environ['admins']:
                if message['text'].lower().startswith('/logs'):
                    text = Auth.logs.text()

                elif message['text'].lower().startswith('/reboot'):
                    text, log_text = Auth.logs.reboot(dispatcher)
        else:
            log_text = ' [#Впервые]'
            text = first_start(message)
        await sender(message, user, text=text, log_text=log_text)
        db.close()
    except IndexError and Exception:
        await Auth.dev.async_except(message)


def google_update():
    global google_users_ids
    while True:
        try:
            sleep(2)
            db = SQL(db_path)
            users = db.get_updates()
            if len(users) > 0:
                client = gspread.service_account('forwarding.json')
                worksheet = client.open('UNITED USERS').worksheet(os.environ['sheet'])
                for user in users:
                    del user['updates']
                    if str(user['id']) in google_users_ids:
                        text = 'обновлен'
                        row = google_users_ids.index(str(user['id'])) + 1
                    else:
                        text = 'добавлен'
                        row = len(google_users_ids) + 1
                        google_users_ids.append(str(user['id']))
                    google_row = f'A{row}:{ascii_uppercase[len(user)-1]}{row}'

                    try:
                        user_range = worksheet.range(google_row)
                    except IndexError and Exception as error:
                        if 'exceeds grid limits' in str(error):
                            worksheet.add_rows(1000)
                            user_range = worksheet.range(google_row)
                            sleep(5)
                        else:
                            raise error

                    for index, value, col_type in zip(range(len(user)), user.values(), users_columns):
                        value = Auth.time(value, form='iso', sep='_') if '<DATE>' in col_type else value
                        value = 'None' if value is None else value
                        user_range[index].value = value
                    worksheet.update_cells(user_range)
                    db.update('users', user['id'], {'updates': 0}, True)
                    Auth.dev.printer(f"Пользователь {text} {user['id']}")
                    sleep(1)
        except IndexError and Exception:
            Auth.dev.thread_except()


def auto_reboot():
    global logging
    reboot = None
    while True:
        try:
            sleep(30)
            date = datetime.now(tz)
            if date.strftime('%H') == '23' and date.strftime('%M') == '57':
                reboot = True
                while date.strftime('%M') == '57':
                    sleep(1)
                    date = datetime.now(tz)
            if reboot:
                reboot = None
                text, _ = Auth.logs.reboot(dispatcher)
                Auth.dev.printer(text)
        except IndexError and Exception:
            Auth.dev.thread_except()


def logger():
    global logging
    while True:
        try:
            log = copy(logging)
            logging = []
            Auth.logs.send(log)
        except IndexError and Exception:
            Auth.dev.thread_except()


def start(stamp):
    global start_message
    if os.environ.get('local'):
        threads = [logger, google_update]
        Auth.dev.printer(f'Запуск бота локально за {time_now() - stamp} сек.')
    else:
        start_message = Auth.dev.start(stamp)
        threads = [logger, google_update, auto_reboot]
        Auth.dev.printer(f'Бот запущен за {time_now() - stamp} сек.')

    for thread_element in threads:
        _thread.start_new_thread(thread_element, ())
    executor.start_polling(dispatcher, allowed_updates=functions.allowed_updates)


if __name__ == '__main__' and os.environ.get('local'):
    start(stamp1)
