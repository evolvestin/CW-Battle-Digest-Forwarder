import os
import re
import asyncio
import objects
import _thread
import gspread
from time import sleep
from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from objects import bold, code, time_now, html_link, html_secure

stamp1 = time_now()
objects.environmental_files()
search_block_pattern = 'initiate conversation with a user|user is deactivated|Have no rights' \
                       '|The group has been migrated|bot was kicked from the supergroup chat' \
                       '|bot was blocked by the user|Chat not found|bot was kicked from the group chat'
media_contents = ['photo', 'document', 'animation', 'voice', 'audio', 'video', 'video_note',
                  'dice', 'poll', 'sticker', 'location', 'contact', 'new_chat_photo', 'game']
red_contents = [*media_contents, 'new_chat_members', 'left_chat_member', 'new_chat_title', 'delete_chat_photo',
                'group_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message']
idChannelForward = -1001449490549
idChannelMedia = -1001273330143
idChannelDump = -1001200576139
idChannelMain = -1001492730228
idMe = 396978030
db = {}
# ====================================================================================
worksheet = gspread.service_account('forwarding.json').open('FORWARDING').worksheet('main')
resources = worksheet.get('A1:Z50000', major_dimension='ROWS')
google_users_ids = worksheet.col_values(1)
options = resources.pop(0)
options.pop(0)
for chat in resources:
    chat_id = int(chat.pop(0))
    db[chat_id] = {}
    for option in options:
        db[chat_id][option] = chat[options.index(option)]
    if 'update' not in db[chat_id]:
        db[chat_id]['update'] = 0

Auth = objects.AuthCentre(os.environ['TOKEN'])
bot = Auth.start_main_bot('async')
dispatcher = Dispatcher(bot)
# ====================================================================================
start_message = Auth.start_message(stamp1)


def header(sign, date=None, custom_text=''):
    sign = dict(sign)
    full_head = ''
    response = ''
    if date:
        response += objects.log_time(date, code) + custom_text
    if sign.get('first_name'):
        full_head += sign['first_name'] + ' '
    if sign.get('last_name'):
        full_head += sign['last_name'] + ' '
    if sign.get('title'):
        full_head += sign['title'] + ' '
    full_name = full_head
    full_head += '[@'
    if sign.get('username'):
        full_head += sign['username'] + '] '
        true_username = sign['username']
    else:
        true_username = 'None'
        full_head += '] '
    response += html_secure(full_head) + code(sign['id']) + ':'
    full_name = re.sub('\'', '&#39;', full_name.strip())
    return response, html_secure(full_name), true_username


async def log_data(message):
    text = ''
    space = ''
    media_link = 'https://t.me/'
    user = db.get(message['chat']['id'])
    head, name, username = header(message['chat'], dict(message).get('date'))

    if user:
        if name != user['name'] or username != user['username'] or user['blocked'] == '🅾️':
            user['name'] = name
            user['update'] = 1
            user['username'] = username
            if user['blocked'] == '🅾️':
                user['blocked'] = '♿'

    if message['chat']['id'] < 0 and message['from']:
        space = '     '
        head_name, name, username = header(message['from'])
        head += '\n' + space + '👤 ' + head_name

    if message['forward_from'] or message['forward_from_chat']:
        f_message = await bot.forward_message(idChannelForward, message['chat']['id'], message['message_id'])
        forward = message['forward_from']
        forward_space = space
        f_link = media_link
        space += '     '
        if message['forward_from_chat']:
            forward = message['forward_from_chat']
        if f_message['chat']['username']:
            f_link += f_message['chat']['username']
        else:
            f_link += 'c/' + re.sub('-100', '', str(f_message['chat']['id']))
        f_link = ' ' + html_link(f_link + '/' + str(f_message['message_id']), 'Форвард') + ' от '
        head_name, name, username = header(forward, dict(message).get('forward_date'), '\n' + space)
        head += '\n' + forward_space + code('&#62;&#62;') + f_link + head_name

    head = '\n' + head + '\n' + space + code('&#62;&#62;') + ' '
    space += '      '

    if message['text'] or message['caption']:
        if message['text']:
            text_list = list(html_secure(message['text']))
            entities = message['entities']
        else:
            text_list = list(html_secure(message['caption']))
            entities = message['caption_entities']
            text += '\n'
        if entities:
            position = 0
            used_offsets = []
            for i in text_list:
                true_length = len(i.encode('utf-16-le')) // 2
                while true_length > 1:
                    text_list.insert(position + 1, '')
                    true_length -= 1
                position += 1
            for i in reversed(entities):
                end_index = i.offset + i.length - 1
                if i.offset + i.length >= len(text_list):
                    end_index = len(text_list) - 1
                if i.type != 'mention':
                    tag = 'code'
                    if i.type == 'bold':
                        tag = 'b'
                    elif i.type == 'italic':
                        tag = 'i'
                    elif i.type == 'text_link':
                        tag = 'a'
                    elif i.type == 'underline':
                        tag = 'u'
                    elif i.type == 'strikethrough':
                        tag = 's'
                    if i.offset + i.length not in used_offsets or i.type == 'text_link':
                        text_list[end_index] += '</' + tag + '>'
                        if i.type == 'text_link':
                            tag = 'a href="' + i.url + '"'
                        text_list[i.offset] = '<' + tag + '>' + text_list[i.offset]
                        used_offsets.append(i.offset + i.length)
        text += ''.join(text_list)
        text = re.sub('\n', '\n' + space, text)

    if message['pinned_message']:
        text += bold('Запинил сообщение:')
        pinned = await log_data(message['pinned_message'])
        text += re.sub('\n', '\n' + space, pinned)

    if message['new_chat_title']:
        text += bold('Изменил название чата')
    elif message['delete_chat_photo']:
        text += bold('Удалил аватарку чата')
    elif message['group_chat_created']:
        text += bold('Создал группу')
    elif message['migrate_to_chat_id']:
        text += bold('Последнее сообщение в чате. Группа стала супергруппой:\n') + space + \
            'Новый ID:' + code(' ' + str(message['migrate_to_chat_id']))
    elif message['migrate_from_chat_id']:
        text += bold('Создана супергруппа.\n') + space + \
            'Старый ID:' + code(' ' + str(message['migrate_from_chat_id']))
    elif message['new_chat_members'] or message['left_chat_member']:
        members = []
        if message['left_chat_member']:
            member = dict(message['left_chat_member'])
            member['left'] = True
            members.append(member)
        else:
            for member in message['new_chat_members']:
                members.append(dict(member))
        for member in members:
            for attr in ['first_name', 'last_name', 'username']:
                if member.get(attr) is None:
                    member[attr] = None
            if member.get('left'):
                if message['from']['id'] == member['id']:
                    text += bold('Вышел из чата')
                else:
                    text += bold('Кикнул {} из чата')
            else:
                if message['from']['id'] == member['id']:
                    text += bold('Зашел в чат по ссылке')
                else:
                    text += bold('Добавил {} в чат')
            if message['from']['id'] != member['id']:
                head_name, name, username = header(member)
                if member['is_bot'] is True:
                    emoji = '🤖 '
                    text = text.format('бота')
                    if username == str(Auth.get_me.get('username')):
                        text += ' #Я'
                else:
                    emoji = '👤 '
                    text = text.format('пользователя')
                text += '\n' + space + emoji + head_name[:-1]

    for message_type in media_contents:
        if message[message_type]:
            postfix = ''
            caption = re.sub('\n' + space, '\n', text)
            text = 'Прислал #медиа в виде {}{}' + text
            if message['caption']:
                postfix += ' с подписью:'
            if message['forward_from_chat']:
                channel = message['forward_from_chat']
                text += '\n' + space + 'https://t.me/' + str(channel['username']) + '/' + \
                    str(message['forward_from_message_id'])

            if message_type == 'photo':
                doc_type = bold('ФОТКИ') + ' #фото'
                file_id = message['photo'][len(message['photo']) - 1]['file_id']
                media = await bot.send_photo(idChannelMedia, file_id, caption, parse_mode='HTML')

            elif message_type == 'document':
                file_id = message['document']['file_id']
                doc_type = bold('ДОКУМЕНТА') + ' #документ'
                if message['animation']:
                    text = re.sub(r'Прислал #медиа в виде [{}]{4}', '', text, 1)
                    continue
                media = await bot.send_document(idChannelMedia, file_id, caption=caption, parse_mode='HTML')

            elif message_type == 'animation':
                doc_type = bold('ГИФКИ') + ' #гифка'
                file_id = message['animation']['file_id']
                media = await bot.send_document(idChannelMedia, file_id, caption=caption, parse_mode='HTML')

            elif message_type == 'voice':
                doc_type = bold('ВОЙСА') + ' #войс'
                file_id = message['voice']['file_id']
                media = await bot.send_voice(idChannelMedia, file_id, caption, parse_mode='HTML')

            elif message_type == 'audio':
                doc_type = bold('АУДИО') + ' #аудио'
                file_id = message['audio']['file_id']
                media = await bot.send_audio(idChannelMedia, file_id, caption, parse_mode='HTML')

            elif message_type == 'video':
                doc_type = bold('ВИДЕО') + ' #видео'
                file_id = message['video']['file_id']
                media = await bot.send_video(idChannelMedia, file_id, caption=caption, parse_mode='HTML')

            elif message_type == 'video_note':
                file_id = message['video_note']['file_id']
                doc_type = bold('ВИДЕО-СООБЩЕНИЯ') + ' #видеосообщение'
                media = await bot.send_video_note(idChannelMedia, file_id)

            elif message_type == 'dice':
                doc_type = bold('ИГРАЛЬНОЙ КОСТИ') + ' #кость #dice'
                media = await bot.forward_message(idChannelMedia, message['chat']['id'], message['message_id'])

            elif message_type == 'poll':
                doc_type = bold('ГОЛОСОВАНИЯ')
                if message['poll']['type'] == 'quiz':
                    doc_type = bold('КВИЗА')
                doc_type += ' #голосование #квиз'
                media = await bot.forward_message(idChannelMedia, message['chat']['id'], message['message_id'])

            elif message_type == 'sticker':
                file_id = message['sticker']['file_id']
                doc_type = bold('СТИКЕРА') + ' #стикер'
                text += '\n' + space + 'https://t.me/addstickers/' + str(message['sticker']['set_name'])
                media = await bot.send_sticker(idChannelMedia, file_id)

            elif message_type == 'location':
                doc_type = bold('АДРЕСА') + ' #адрес'
                file_id = message['location']['latitude'], message['location']['longitude']
                media = await bot.send_location(idChannelMedia, *file_id)

            elif message_type == 'contact':
                doc_type = bold('КОНТАКТА') + ' #контакт'
                name = message['contact']['first_name']
                if message['contact']['last_name']:
                    name += message['contact']['last_name']
                if message['contact']['user_id']:
                    text += '\n' + space + 'ID пользователя: ' + code(message['contact']['user_id'])
                media = await bot.forward_message(idChannelMedia, message['chat']['id'], message['message_id'])

            elif message_type == 'new_chat_photo':
                doc_type = 'новой ' + bold('АВАТАРКИ') + ' чата #фото #ава'
                head_name, name, username = header(message['chat'])
                caption = 'Новая #аватарка в чате:\n' + head_name[:-1]
                file_id = message['new_chat_photo'][len(message['new_chat_photo']) - 1]['file_id']
                media = await bot.send_photo(idChannelMedia, file_id, caption, parse_mode='HTML')

            elif message_type == 'game':
                doc_type = bold('ИГРЫ') + ' #игра #game'
                media = await bot.forward_message(idChannelMedia, message['chat']['id'], message['message_id'])
            else:
                doc_type = 'None'
                media = message

            if media['chat']['username']:
                media_link += media['chat']['username']
            else:
                media_link += 'c/' + re.sub('-100', '', str(media['chat']['id']))
            reply_text, name, username = header(Auth.get_me)
            media_link += '/' + str(media['message_id'])
            text = text.format(doc_type, postfix)
            text += '\n' + space + media_link
            reply_text += head + text
            await bot.send_message(idChannelMedia, reply_text, disable_web_page_preview=True,
                                   reply_to_message_id=media['message_id'], parse_mode='HTML')
    return head + text


async def sender(message, text=None, log_text=''):
    if text:
        try:
            await bot.send_message(message['chat']['id'], text, disable_web_page_preview=True, parse_mode='HTML')
        except IndexError and Exception as error:
            search_retry = re.search(r'Retry in (\d+) seconds', str(error))
            search_block = re.search(search_block_pattern, str(error))
            if search_retry:
                await asyncio.sleep(int(search_retry.group(1)) + 1)
                await sender(message, text, log_text='False')
            elif search_block:
                db[message['chat']['id']]['blocked'] = '🅾️'
                db[message['chat']['id']]['update'] = 1
                if log_text != 'False':
                    log_text += bold(' [Не доставлено]')
            else:
                error_text = 'Not delivered: ' + str(message['chat']['id']) + '\n' + str(error) + '\n'
                error_text += 'len(re.sub(<.*?>, text)) = ' + str(len(re.sub('<.*?>', '', text)))
                error_text += 'len(text) = ' + str(len(str(text))) + '\n'
                await Auth.async_exec(error_text + str(text))
    if log_text != 'False':
        try:
            logs = await log_data(message)
        except IndexError and Exception as error:
            search_retry = re.search(r'Retry in (\d+) seconds', str(error))
            logs = False
            if search_retry:
                await asyncio.sleep(int(search_retry.group(1)) + 1)
                await sender(message, log_text)
            else:
                await Auth.async_exec(str(error))
        if logs:
            logs += log_text
            if len(re.sub('<.*?>', '', logs)) <= 4096:
                await bot.send_message(idChannelDump, logs, disable_web_page_preview=True, parse_mode='HTML')
            else:
                try:
                    for factor in range(0, 2):
                        temp_text = logs[factor * 4096:(factor + 1) * 4096]
                        if temp_text:
                            await bot.send_message(idChannelDump, temp_text,
                                                   disable_web_page_preview=True, parse_mode='HTML')
                except IndexError and Exception as error:
                    await Auth.async_exec(str(error))


@dispatcher.channel_post_handler()
async def repeat_channel_messages(message: types.Message):
    global start_message
    try:
        if message['chat']['id'] == idChannelMain:
            is_message_actual_to_send = False
            search = re.search(r'Битва (\d{2}/\d{2}/\d{4} \d{2}:\d{2})', message['text'])
            if search:
                battle_stamp = objects.stamper(search.group(1), '%d/%m/%Y %H:%M') - 3 * 60 * 60
                if (time_now() - battle_stamp) < 1800 and (time_now() - dict(message).get('date')) < 1800:
                    is_message_actual_to_send = True

            if is_message_actual_to_send:
                stamp = time_now()
                send_pointer = 0
                for user_id in db:
                    if db[user_id]['blocked'] != '🅾️':
                        try:
                            await bot.forward_message(user_id, idChannelMain, message['message_id'])
                            send_pointer += 1
                        except IndexError and Exception as error:
                            search_retry = re.search(r'Retry in (\d+) seconds', str(error))
                            search_block = re.search(search_block_pattern, str(error))
                            if search_retry:
                                await asyncio.sleep(int(search_retry.group(1)) + 1)
                                await bot.forward_message(user_id, idChannelMain, message['message_id'])
                            elif search_block:
                                db[user_id]['blocked'] = '🅾️'
                                db[user_id]['update'] = 1
                            else:
                                error_text = 'Not delivered: ' + str(message['chat']['id']) + '\n' + str(error) + '\n'
                                await Auth.async_exec(error_text)
                text = bold('\n\nОтправка сводок:\n1.') + objects.log_time(stamp, code) + \
                    bold('\n' + str(send_pointer) + '. ') + objects.log_time(time_now(), code)
                start_message = Auth.edit_dev_message(start_message, text)
        else:
            if db.get(message['chat']['id']):
                await sender(message)
            else:
                await first_start(message, send_text=False)
                await sender(message, '✅', log_text='False')
    except IndexError and Exception:
        await Auth.async_exec(str(message))


async def first_start(message, send_text=True):
    eng_description = 'Promote bot to admin just in case. Chat already subscribed to new battle digests.'
    rus_description = 'Дайте боту права администратора на всякий случай. Чат уже добавлен в рассылку.'
    text = code('//') + bold(eng_description + '\n') + code('//') + bold(rus_description + '\n')
    head, name, username = header(message['chat'])
    log_text = ''
    if message['chat']['id'] not in db:
        log_text = bold(' [Впервые]')
        db[message['chat']['id']] = {
            'name': name,
            'username': username,
            'blocked': '✅',
            'update': 1}
    if send_text:
        await sender(message, text, log_text)
    else:
        await sender(message, log_text=log_text)


@dispatcher.message_handler(content_types=red_contents)
async def red_messages(message: types.Message):
    try:
        if message['new_chat_members']:
            for member in message['new_chat_members']:
                head_name, name, username = header(member)
                if username == str(Auth.get_me.get('username')):
                    await first_start(message)
                else:
                    await sender(message)
        elif message['group_chat_created']:
            await first_start(message)
        elif message['migrate_from_chat_id']:
            await asyncio.sleep(5)
            await first_start(message, send_text=False)
        elif message['migrate_to_chat_id']:
            await sender(message)
            user = db[message['chat']['id']]
            user['username'] = 'DISABLED_GROUP'
            user['blocked'] = '🅾️'
            user['update'] = 1
        else:
            await sender(message)
    except IndexError and Exception:
        await Auth.async_exec(str(message))


@dispatcher.message_handler()
async def repeat_all_messages(message: types.Message):
    try:
        if db.get(message['chat']['id']):
            if message['chat']['id'] == idMe:
                if message['text'].lower().startswith('/log'):
                    await bot.send_document(message['chat']['id'], open('log.txt', 'rb'))
                elif message['text'].lower().startswith('/h'):
                    for i in db:
                        print(str(i) + ':', db.get(i))
                else:
                    await sender(message)
            elif message['text'].lower().startswith('/start'):
                await first_start(message)
            elif message['text'].lower().startswith('/reg'):
                await sender(message, '✅')
            else:
                await sender(message)
        else:
            send_text = False
            if message['text'].lower().startswith('/start'):
                send_text = True
            await first_start(message, send_text=send_text)
    except IndexError and Exception:
        await Auth.async_exec(str(message))


def google():
    global google_users_ids, worksheet
    while True:
        try:
            sleep(3)
            worksheet = gspread.service_account('forwarding.json').open('FORWARDING').worksheet('main')
            for user_id in db:
                user = db[user_id]
                if user['update'] == 1:
                    if str(user_id) in google_users_ids:
                        row = str(google_users_ids.index(str(user_id)) + 1)
                        print_text = ' обновлен '
                    else:
                        row = str(len(google_users_ids) + 1)
                        google_users_ids.append(str(user_id))
                        print_text = ' добавлен '
                    user_range = worksheet.range('A' + row + ':D' + row)
                    user_range[0].value = int(user_id)
                    for i in range(1, len(user)):
                        user_range[i].value = list(user.values())[i - 1]
                    objects.printer('пользователь' + print_text + str(user_id))
                    worksheet.update_cells(user_range)
                    user['update'] = 0
                    sleep(1)
        except IndexError and Exception:
            Auth.thread_exec()


if __name__ == '__main__':
    _thread.start_new_thread(google, ())
    executor.start_polling(dispatcher)
