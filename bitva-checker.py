import re
import sys
import _thread
import telebot
import requests
import datetime
import traceback
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup

stamp1 = int(datetime.now().timestamp())
start_link = 'https://t.me/UsefullCWLinks/4?embed=1'
adress = 'https://t.me/ChatWarsDigest/'
title = '<b>⛳️Сводки с полей:</b>\n'
idChannel = -1001492730228
idMe = 396978030
server = 'CW3'
post = 0

start_text = requests.get(start_link)
start = BeautifulSoup(start_text.text, 'html.parser')
start = str(start.find('div', class_='tgme_widget_message_text js-message_text'))
start = re.sub('(<b>|</b>|<code>|</code>|</div>)', '', start)
start_srch = re.search(server + ': (\d+) :' + server, start)

if start_srch:
    post = int(start_srch.group(1))
    tkn = '512299506:AAGwDkft8yr0dSknOC8gCdf_cFU6civ3jls'
    bot = telebot.TeleBot(tkn)
    start_message = bot.send_message(idMe, '🧠', parse_mode='HTML')
else:
    print('Ошибка с нахождением номера поста')
    _thread.exit()


e_trident = '🔱'
castles = '(🐢|☘️|🌹|🍁|🦇|🖤|🍆)'
character = {
    'успешно атаковали защитников': '⚔',
    'со значительным преимуществом': '⚔😎',
    'разыгралась настоящая бойня, но все-таки силы атакующих были ': '⚔⚡',
    'успешно отбились от': '🛡',
    'легко отбились от': '🛡👌',
    'героически отразили ': '🛡⚡',
    'скучали, на них ': '🛡😴',
}


# ====================================================================================


def timer(search):
    s_day = int(search.group(1))
    s_month = str(search.group(2))
    s_year = int(search.group(3)) - 60
    stamp = int(datetime.now().timestamp())
    sec = ((stamp + (2 * 60 * 60) - 1530309600) * 3)
    if s_month == 'Wintar':
        month = 1
    elif s_month == 'Hornung':
        month = 2
    elif s_month == 'Lenzin':
        month = 3
    elif s_month == 'Ōstar':
        month = 4
    elif s_month == 'Winni':
        month = 5
    elif s_month == 'Brāh':
        month = 6
    elif s_month == 'Hewi':
        month = 7
    elif s_month == 'Aran':
        month = 8
    elif s_month == 'Witu':
        month = 9
    elif s_month == 'Wīndume':
        month = 10
    elif s_month == 'Herbist':
        month = 11
    elif s_month == 'Hailag':
        month = 12
    else:
        month = 0

    if month != 0:
        day31 = 31 * 24 * 60 * 60
        day30 = 30 * 24 * 60 * 60
        day28 = 28 * 24 * 60 * 60
        seconds = 0 - (24 * 60 * 60)
        if s_year == 4:
            day28 = day28 + 24 * 60 * 60
        elif s_year > 4:
            seconds = seconds + 24 * 60 * 60
        seconds = seconds + day30 + day31 + 31536000 * (s_year - 1)  # Wīndume
        if month == 1:
            seconds = seconds
        elif month == 2:
            seconds = seconds + day31
        elif month == 3:
            seconds = seconds + day31 + day28
        elif month == 4:
            seconds = seconds + day31 + day28 + day31
        elif month == 5:
            seconds = seconds + day31 + day28 + day31 + day30
        elif month == 6:
            seconds = seconds + day31 + day28 + day31 + day30 + day31
        elif month == 7:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30
        elif month == 8:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31
        elif month == 9:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31
        elif month == 10:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30
        elif month == 11:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31
            if s_year == 0:
                seconds = 0 - (24 * 60 * 60)
        elif month == 12:
            seconds = seconds + day31 + day28 + day31 + day30 + day31 + day30 + day31 + day31 + day30 + day31 + day30
            if s_year == 0:
                seconds = day30 - (24 * 60 * 60)

        seconds = seconds + s_day * 24 * 60 * 60
        stack = int(stamp + (seconds - sec) / 3) + 2 * 60 * 60
        day = datetime.utcfromtimestamp(int(stack + 3 * 60 * 60)).strftime('%d')
        month = datetime.utcfromtimestamp(int(stack + 3 * 60 * 60)).strftime('%m')
        years = datetime.utcfromtimestamp(int(stack + 3 * 60 * 60)).strftime('%Y')
        hours = datetime.utcfromtimestamp(int(stack + 3 * 60 * 60)).strftime('%H')
        minutes = datetime.utcfromtimestamp(int(stack)).strftime('%M')
        time = '<i>' + str(day) + '/' + str(month) + '/' + str(years) + ' ' + str(hours) + ':' + str(minutes) + '</i>'
        return time


def executive(name):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = ''
    for i in error_raw:
        error += str(i)
    bot.send_message(idMe, 'Вылет ' + name + '\n' + error)
    _thread.exit()


def checker():
    while True:
        try:
            global stamp_checker
            global post
            stamp_checker = int(datetime.now().timestamp())
            sleep(0.1)
            text = requests.get(adress + str(post) + '?embed=1')
            soup = BeautifulSoup(text.text, 'html.parser')
            is_post_exist = str(soup.find('div', class_='tgme_widget_message_text js-message_text'))
            if str(is_post_exist) != 'None':
                print('работаю ' + adress + str(post))
                soup = str(soup.find('div', class_='tgme_widget_message_text js-message_text'))
                time_search = re.search('(\d\d) (.*) 10(..).*Результаты сражений:', soup)
                if time_search:
                    soup = re.sub('.*Результаты сражений:</b><br/>', '', soup)
                    splited = re.split('<br/><br/>', soup)
                    trophy_search = None
                    reports = {}
                    final = ''
                    for i in splited:
                        string = re.sub(' (class|style)=\\"\w+[^\\"]+\\"', '', i)
                        trophy_search = re.search('По итогам сражений замкам начислено:<br/>(.*)', string)
                        string = re.sub('По итогам сражений замкам начислено:.+', '', string)
                        string = re.sub('(<br/>|<b>|</b>|<i>|</i>)', '', string)
                        string = re.sub('🎖Лидеры.+🏆', '', string)
                        search = re.search(castles, string)
                        if search:
                            mini = 'NaN'
                            for m in character:
                                if m in string:
                                    mini = character.get(m)
                                    if e_trident in string:
                                        mini = e_trident + mini

                            money_search = re.search('(на|отобрали) (.*) золотых монет', string)
                            if money_search:
                                if money_search.group(1) == 'на':
                                    mini += ' -' + money_search.group(2) + '💰'
                                elif money_search.group(1) == 'отобрали':
                                    mini += ' +' + money_search.group(2) + '💰'

                            box_search = re.search('потеряно (.*) складских ячеек', string)
                            if box_search:
                                if box_search.group(1) != '0':
                                    box = ' -' + box_search.group(1) + '📦'
                                else:
                                    box = ''
                                mini += box
                            reports.update({search.group(1)[:1]: ': ' + mini})

                    if trophy_search:
                        stamp_checker = int(datetime.now().timestamp())
                        trophy = re.split('<br/>', trophy_search.group(1))
                        for i in trophy:
                            castle_tr = re.sub('(<b>|</b>|<i>|</i>|</div>)', '', i)
                            search = re.search(castles + '.+ \+(\d+) 🏆 очков', castle_tr)
                            if search:
                                castle = search.group(1)
                                if castle == '☘️':
                                    castle = '☘'
                                final += '<i>' + castle + str(reports.get(castle)) + ' +' + search.group(2) + '🏆</i>\n'

                        if final != '':
                            letter = title + final + \
                                     '<a href="' + adress + str(post) + '">Битва</a> ' + timer(time_search)
                        else:
                            letter = 'Ошибка, нет текста сообщения'
                            bot.send_message(idMe, letter, parse_mode='HTML', disable_web_page_preview=True)
                        try:
                            bot.send_message(idChannel, letter, parse_mode='HTML', disable_web_page_preview=True)
                            sleep(4)
                            post += 1
                            try:
                                start_editing = '<b>' + server + ':</b> <code>' + \
                                                str(post) + '</code> :<b>' + server + '</b>'
                                bot.edit_message_text(start_editing, -1001471643258, 4, parse_mode='HTML')
                            except:
                                error = '<b>Проблемы с измением стартового ' \
                                        'сообщения на канале @UsefullCWLinks</b>\n\n' + letter
                                bot.send_message(idMe, error, parse_mode='HTML', disable_web_page_preview=True)
                        except:
                            error = '<b>Проблемы с отправкой на канал, перезапускаю</b>\n\n' + letter
                            bot.send_message(idMe, error, parse_mode='HTML', disable_web_page_preview=True)
                            _thread.exit()
                    else:
                        bot.send_message(idMe, 'Что-то пошло не так, проблемы с поиском инфы в посте, перезапускаю')
                        _thread.exit()
                else:
                    print('пост ' + adress + str(post) + ' не относится к дайджесту, пропускаю')
                    post += 1
            else:
                print('поста нет ' + adress + str(post))
        except IndexError:
            thread_name = 'checker'
            executive(thread_name)


def starter():
    while True:
        try:
            sleep(200)
            global stamp_checker
            thread_name = 'starter '
            print(thread_name + 'начало')
            now = int(datetime.now().timestamp()) - 100
            if now > stamp_checker:
                _thread.start_new_thread(stamp_checker, ())
                print('запуск stamp_checker')
            print(thread_name + 'конец')
            sleep(100)
        except IndexError:
            thread_name = 'starter'
            executive(thread_name)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    _thread.start_new_thread(checker, ())
    _thread.start_new_thread(starter, ())
    telepol()
