import re
import sys
import copy
import json
import _thread
import gspread
import telebot
import datetime
import traceback
import unicodedata
from time import sleep
from datetime import datetime
from unidecode import unidecode
from collections import defaultdict
from oauth2client.service_account import ServiceAccountCredentials

stamp1 = int(datetime.now().timestamp())
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('forwarding.json', scope)
client = gspread.authorize(creds)
dater = client.open('FORWARDING').worksheet('main')
tkn = '913645382:AAHJaL1PxvGQVkJcn7mLvhQzmQpxgBcfJpE'  # CWDailyBot (@CWDailyBot)
bot = telebot.TeleBot(tkn)

g_users = dater.col_values(1)
g_ids = dater.col_values(2)
g_block = dater.col_values(3)
g_users.pop(0)
g_ids.pop(0)
g_block.pop(0)

idChannelForward = -1001449490549
idChannelMedia = -1001273330143
idChannelMain = -1001492730228
idChannelDump = -1001200576139
array = defaultdict(dict)
botname = 'CWDailyBot'
idMe = 396978030
server = 'CW3'


to_chat = '<code>//</code><b>Promote bot to admin just in case and press:</b>\n' \
          '<code>//</code><b>Дайте боту права администратора на всякий случай и нажмите:</b>\n' \
          '/reg@' + botname

for i in g_ids:
    array[int(i)] = defaultdict(dict)
    array[int(i)]['name'] = g_users[g_ids.index(i)]
    array[int(i)]['block'] = g_block[g_ids.index(i)]
    array[int(i)]['update'] = 0
# ====================================================================================


def logtime(stamp):
    if stamp == 0:
        stamp = int(datetime.now().timestamp())
    weekday = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%a')
    if weekday == 'Mon':
        weekday = 'Пн'
    elif weekday == 'Tue':
        weekday = 'Вт'
    elif weekday == 'Wed':
        weekday = 'Ср'
    elif weekday == 'Thu':
        weekday = 'Чт'
    elif weekday == 'Fri':
        weekday = 'Пт'
    elif weekday == 'Sat':
        weekday = 'Сб'
    elif weekday == 'Sun':
        weekday = 'Вс'
    day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
    year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stamp)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stamp)).strftime('%S')
    data = '<code>' + str(weekday) + ' ' + str(day) + '.' + str(month) + '.' + str(year) + \
           ' ' + str(hours) + ':' + str(minutes) + ':' + str(seconds) + '</code> '
    return data


start_message = bot.send_message(idMe, logtime(stamp1) + '\n' + logtime(0), parse_mode='HTML')
# ====================================================================================


def executive(e, name, message):
    if message != 0:
        text = ''
        for character in message:
            replaced = unidecode(str(character))
            if replaced != '':
                text += replaced
            else:
                try:
                    text += '[' + unicodedata.name(character) + ']'
                except ValueError:
                    text += '[???]'
        docw = open(name + '.json', 'w')
        docw.write(text)
        docw.close()
        doc = open(name + '.json', 'rb')
        bot.send_document(idMe, doc)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = ''
    for i in error_raw:
        error += str(i)
    try:
        jsoner = json.loads(str(e))
        bot.send_message(idMe, 'Вылет ' + name + '\n' + error)
        if 'error' in jsoner:
            if jsoner['error']['status'] == 'RESOURCE_EXHAUSTED':
                sleep(100)
            elif jsoner['error']['status'] == 'UNAVAILABLE' or jsoner['error']['status'] == 'UNAUTHENTICATED':
                sleep(20)
    except:
        bot.send_message(idMe, 'Вылет ' + name + '\n' + error)
    if message == 0:
        _thread.exit()


def logdata(message):
    global data
    global encode
    data = logtime(message.date)
    pr = ''
    encode = ''
    if message != 0:
        if message.chat.id in array:
            if str(array[message.chat.id]['block']) == '🅾️':
                array[message.chat.id]['block'] = '⚠️'
                array[message.chat.id]['update'] = 1
        encode = message
        try:
            kind = message.chat
            if message.chat.id < 0:
                kind = message.from_user
        except:
            kind = message.from_user
        firstname = ''
        lastname = ''
        username = ''
        if kind.first_name:
            firstname = str(kind.first_name) + ' '
        if kind.last_name:
            lastname = str(kind.last_name) + ' '
        if kind.username:
            username = str(kind.username)
        if message.chat.id < 0:
            title = ''
            chat_user = ''
            if message.chat.title:
                title = str(message.chat.title) + ' '
                title = re.sub('[<>]', '', title)
                if message.chat.id in array:
                    if str(array[message.chat.id]['name']) != message.chat.title:
                        array[message.chat.id]['name'] = message.chat.title
                        array[message.chat.id]['update'] = 1
            if message.chat.username:
                chat_user = str(message.chat.username)
            chat_id = str(message.chat.id)
            chat = title + '[@' + chat_user + '] <code>' + chat_id + '</code>:\n     👤 '
            tl = '     '
            pr = '     '
        else:
            name = '@'
            if message.chat.username:
                name += message.chat.username
            if message.chat.id in array:
                if str(array[message.chat.id]['name']) != username:
                    array[message.chat.id]['name'] = name
                    array[message.chat.id]['update'] = 1
            chat = ''
            pr = ''
            tl = ''
        if message.forward_from:
            fw_data = logtime(message.forward_date)
            forw = message.forward_from
            fw_firstname = ''
            fw_lastname = ''
            fw_username = ''
            if forw.first_name:
                fw_firstname = str(forw.first_name) + ' '
            if forw.last_name:
                fw_lastname = str(forw.last_name) + ' '
            if forw.username:
                fw_username = str(forw.username)
            pr = pr + '     '
            bot.forward_message(idChannelForward, message.chat.id, message.message_id)
            cleared_fw_names = re.sub('[<>]', '', fw_firstname + fw_lastname + '[@' + fw_username + ']')
            forward = '<code>&#62;&#62;</code> Форвард от ' + fw_data + '\n' + pr \
                      + cleared_fw_names + ' <code>' + str(forw.id) + '</code>:\n'

        elif message.forward_from_chat:
            fw_data = logtime(message.forward_date)
            forw = message.forward_from_chat
            fw_title = ''
            fw_username = ''
            if forw.title:
                fw_title = forw.title + ' '
                fw_title = re.sub('[<>]', '', fw_title)
            if forw.username:
                fw_username = str(forw.username)
            pr = pr + '     '
            bot.forward_message(idChannelForward, message.chat.id, message.message_id)
            forward = '<code>&#62;&#62;</code> Форвард от ' + fw_data + '\n' + pr \
                      + fw_title + '[@' + fw_username + '] <code>' + str(forw.id) + '</code>:\n'
        else:
            forward = ''
            pr = ''

        cleared_names = re.sub('[<>]', '', firstname + lastname + '[@' + username + ']')
        data = '\n' + data + chat + cleared_names + ' <code>' + \
               str(kind.id) + '</code>:\n' + tl + forward + pr + '<code>&#62;&#62;</code> '

        if message.photo:
            data = data + 'Прислал #медиа в виде <b>ФОТКИ</b> #фото'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_photo(idChannelMedia, message.photo[len(message.photo) - 1].file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.document:
            doc = '<b>ДОКУМЕНТА</b> #документ'
            if message.document.mime_type == 'video/mp4':
                doc = '<b>ГИФКИ</b> #гифка'
            data = data + 'Прислал #медиа в виде ' + doc
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_document(idChannelMedia, message.document.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.voice:
            data = data + 'Прислал #медиа в виде <b>ВОЙСА</b> #войса'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_voice(idChannelMedia, message.voice.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.audio:
            data = data + 'Прислал #медиа в виде <b>АУДИО</b> #аудио'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_audio(idChannelMedia, message.audio.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.video:
            data = data + 'Прислал #медиа в виде <b>ВИДЕО</b> #видео'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_video(idChannelMedia, message.video.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.sticker:
            data = data + 'Прислал #медиа в виде <b>СТИКЕРА</b> #стикер'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_sticker(idChannelMedia, message.sticker.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)

        elif message.video_note:
            data = data + 'Прислал #медиа в виде <b>ВИДЕО-СООБЩЕНИЯ</b> #видеосообщение'
            sup = node(message, data, pr)
            data = sup[0]
            pin = bot.send_video_note(idChannelMedia, message.video_note.file_id, sup[1])
            data = data + '\n' + sup[2] + 'https://t.me/' + pin.chat.username + '/' + str(pin.message_id)
            bot.send_message(idChannelMedia, server, reply_to_message_id=pin.message_id)
    massive = [data, '\n      ' + pr]
    return massive


def node(message, data, pr):
    sp = '      '
    if message.chat.id < 0:
        sp = sp + '     '
    if message.forward_from:
        sp = sp + '     '
    if message.caption:
        cap = str(message.caption)
        pr = pr + '     '
        data = data + ' с припиской:\n' + pr + '<code>---------------</code>\n' + pr + '   ' \
            + str(message.caption) + '\n' + pr + '<code>---------------</code>' + pr
    else:
        cap = None
    if message.forward_from_chat:
        sp = sp + '     '
        fors = message.forward_from_chat
        data = data + '\n' + sp + 'https://t.me/' + str(fors.username) + '/' + str(message.forward_from_message_id)
    array = [data, cap, sp]
    return array


@bot.channel_post_handler(func=lambda message: message.text)
def repeat_channel_messages(message):
    try:
        temp = copy.copy(array)
    except:
        sleep(2)
        temp = copy.copy(array)
    try:
        if message.chat.id == idChannelMain:
            stamp1 = int(datetime.now().timestamp())
            chat = 0
            for i in temp:
                try:
                    if str(temp[i]['block']) == '✅' or str(temp[i]['block']) == '⚠️':
                        bot.forward_message(i, idChannelMain, message.message_id)
                        chat += 1
                except:
                    array[i]['block'] = '🅾️'
                    array[i]['update'] = 1
                    logarray = logdata(0)
                    logtext = logarray[0] + '<b>BOT</b> [@' + botname + ']:\n<code>&#62;&#62;</code> ' + \
                        '<b>Не доставлено:</b> <code>' + str(i) + '</code> ' + str(temp[i]['name'])
                    bot.send_message(idChannelDump, logtext, parse_mode='HTML')
            stamp2 = int(datetime.now().timestamp())
            bot.send_message(idMe, '<b>Отправка сводок:</b>\n<b>1.</b> ' + logtime(stamp1) + '\n<b>' +
                             str(chat) + '.</b> ' + logtime(stamp2), parse_mode='HTML')

    except IndexError and Exception as e:
        thread_name = 'repeat_channel_messages'
        executive(e, thread_name, str(message))


@bot.message_handler(commands=['reg'])
def handle_reg_command(message):
    try:
        logtext = '/reg'
        text = '✅'
        if message.chat.id not in array:
            name = 'None'
            if message.chat.id > 0:
                name = '@'
                if message.chat.username:
                    name = '@' + str(message.chat.username)
            if message.chat.title:
                name = str(message.chat.title)
            name = re.sub('[<>]', '', name)
            array[message.chat.id] = defaultdict(dict)
            array[message.chat.id]['name'] = name
            array[message.chat.id]['block'] = '✅'
            array[message.chat.id]['update'] = 0
            logtext += ' <b>[Впервые]</b>'
        else:
            text += '♿♿'
        bot.send_message(message.chat.id, text, parse_mode='HTML')
        logarray = logdata(message)
        bot.send_message(idChannelDump, logarray[0] + logtext, parse_mode='HTML')
    except IndexError and Exception as e:
        thread_name = 'handle_reg_command'
        executive(e, thread_name, str(message))


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    try:
        logtext = '/start'
        bot.send_message(message.chat.id, to_chat, parse_mode='HTML')
        logarray = logdata(message)
        bot.send_message(idChannelDump, logarray[0] + logtext, parse_mode='HTML')
    except IndexError and Exception as e:
        thread_name = 'handle_reg_command'
        executive(e, thread_name, str(message))


@bot.message_handler(content_types=['new_chat_members'])
def get_new_member(message):
    try:
        if message.new_chat_member is not None:
            if message.new_chat_member.username == botname:
                logtext = '<b>Добавил бота в чат</b> '
                try:
                    bot.send_message(message.chat.id, to_chat, parse_mode='HTML')
                except:
                    logtext = logtext + '<b>[Не отправлено]</b>'

                logarray = logdata(message)
                logtext = logarray[0] + logtext
                bot.send_message(idChannelDump, logtext, parse_mode='HTML')
    except IndexError and Exception as e:
        thread_name = 'get_new_member'
        executive(e, thread_name, str(message))


@bot.message_handler(content_types=['audio', 'video_note', 'photo', 'video', 'document',
                                    'location', 'contact', 'sticker', 'voice'])
def redmessages(message):
    try:
        if message.chat.id != idChannelMedia:
            if message.photo or message.document or message.voice or message.audio \
                    or message.video or message.sticker or message.video_note:
                logarray = logdata(message)
                bot.send_message(idChannelDump, logarray[0], disable_web_page_preview=True, parse_mode='HTML')
    except IndexError and Exception as e:
        thread_name = 'redmessages'
        executive(e, thread_name, str(message))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    if message.chat.id == idMe:
        if str(message.text).startswith('/log'):
            try:
                temps = copy.copy(array)
            except:
                sleep(2)
                temps = copy.copy(array)
            print(temps)
            for i in temps:
                print(str(i) + ': ' + str(temps[i]['name']) + ' [' + str(temps[i]['block']) + ']')
    else:
        try:
            logarray = logdata(message)
            logtext = re.sub('<', '&lt;', message.text)
            logtext = re.sub('>', '&gt;', logtext)
            logtext = re.sub('\n', logarray[1], logtext)
            bot.send_message(idChannelDump, logarray[0] + logtext, parse_mode='HTML')
        except IndexError and Exception as e:
            thread_name = 'repeat_all_messages'
            executive(e, thread_name, str(message))


def creategooglerow():
    while True:
        try:
            global data
            global stamp_creategooglerow
            stamp_creategooglerow = int(datetime.now().timestamp())
            sleep(5)
            try:
                temp = copy.copy(array)
            except:
                sleep(2)
                temp = copy.copy(array)
            try:
                g_ids = dater.col_values(2)
            except:
                creds = ServiceAccountCredentials.from_json_keyfile_name('forwarding.json', scope)
                client = gspread.authorize(creds)
                dater = client.open('FORWARDING').worksheet('main')
                g_ids = dater.col_values(2)
            for i in temp:
                if str(i) not in g_ids:
                    stamp_creategooglerow = int(datetime.now().timestamp())
                    dater.insert_row([str(temp[i]['name']), i, str(temp[i]['block'])], 2)
                    sleep(5)

            stamp_creategooglerow = int(datetime.now().timestamp())
            g_ids = dater.col_values(2)
            for i in temp:
                if temp[i]['update'] == 1:
                    stamp_creategooglerow = int(datetime.now().timestamp())
                    row = str(g_ids.index(str(i)) + 1)
                    try:
                        cell_list = dater.range('A' + row + ':C' + row)
                        cell_list[0].value = str(temp[i]['name'])
                        cell_list[1].value = i
                        cell_list[2].value = str(temp[i]['block'])
                        dater.update_cells(cell_list)
                        array[i]['update'] = 0
                    except IndexError and Exception as e:
                        thread_name = 'creategooglerow (шаг обновления)'
                        executive(e, thread_name, 0)
                    sleep(2)
            sleep(1)

        except IndexError and Exception as e:
            thread_name = 'creategooglerow'
            executive(e, thread_name, 0)


def starter():
    while True:
        try:
            sleep(200)
            global stamp_creategooglerow
            thread_name = 'starter '
            print(thread_name + 'начало')
            now = int(datetime.now().timestamp()) - 100
            if now > stamp_creategooglerow:
                _thread.start_new_thread(creategooglerow, ())
                bot.send_message(idMe, 'запуск creategooglerow')
                print('запуск creategooglerow')
            print(thread_name + 'конец')
            sleep(100)
        except IndexError and Exception as e:
            thread_name = 'creategooglerow'
            executive(e, thread_name, 0)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    _thread.start_new_thread(creategooglerow, ())
    _thread.start_new_thread(starter, ())
    telepol()
