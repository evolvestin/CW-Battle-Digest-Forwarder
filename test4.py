
import re
import requests

from bs4 import BeautifulSoup

'https://t.me/c/1471643258/4'
tkn = '512299506:AAGwDkft8yr0dSknOC8gCdf_cFU6civ3jls'

text = requests.get('https://t.me/UsefullCWLinks/4?embed=1')
start = BeautifulSoup(text.text, 'html.parser')
start = str(start.find('div', class_='tgme_widget_message_text js-message_text'))
start = re.sub('(<b>|</b>|<code>|</code>|</div>)', '', start)
start_srch = re.search('CW3: (\d+) :CW3', start)
if start_srch:
    post = int(start_srch.group(1))
