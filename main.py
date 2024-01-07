import telebot
import schedule
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import helper as h
from matplotlib import pyplot as plt

# Токен вашего Telegram-бота
# BOT_TOKEN = '6390329177:AAGDCqaBc3dsqJmzGlOKgf8j3_ZjxANt4nA'
BOT_TOKEN = '6939782498:AAG3ONAuKGlBHsUT-Wd1g-q_pBmDzz9eyB0'

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('loseweighttrackbot-d7bf5bfe3d2a.json', scope)
client = gspread.authorize(creds)

dicti = {'Дата':["", 0],'Вес':["кг", 0],'Правая ляха':["см", 0],'Левая ляха':["см", 0],'Правая бицуха':["см", 0],
         'Левая бицуха':["см", 0],'Правая икра':["см", 0],'Левая икра':["см", 0],'Шея':["см", 0],'Талия':["см", 0],
         'ИМТ':[r"$кг/м^2$", 0],'Осталось до цели':["кг", 0],'Процент жира':["%", 0]}

height = 0

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    name = message.from_user.first_name

    try:
        sheet = client.open(f'{chat_id}').sheet1
        bot.send_message(chat_id, 'ваша таблица найдена')
        sheet.append_row(list(dicti.keys()))
        client.open(f'{chat_id}').share('yurafed03@gmail.com', perm_type= 'user', role='writer')
        bot.send_message(chat_id, str(sheet.row_values(1)))
        client.del_spreadsheet('1GlcC_N8mrbh4fddIY73XFE8hdrHufUXkS58g--h-bgI')
        client.del_spreadsheet('1akcWZU4DC_psLn7UBcCFkRZnw6ObHkyhMuBGJ4P1-zM')
    except Exception as e:
        sheet = client.create(f'{chat_id}').sheet1
        sheet.append_row(list(dicti.keys()))
        bot.send_message(chat_id, 'создана таблица')
        bot.send_message(chat_id, str(sheet.row_values(1)))

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Добавить данные в таблицу', callback_data='/add'))
    markup.add(telebot.types.InlineKeyboardButton('Посмотреть данные таблицы', callback_data='/view'))
    markup.add(telebot.types.InlineKeyboardButton('Посмотреть данные таблицы другого человека', callback_data='/view_other'))
    markup.add(telebot.types.InlineKeyboardButton('Построить график параметра', callback_data='/plot'))
    markup.add(telebot.types.InlineKeyboardButton('Построить график параметра другого человека', callback_data='/plot_other'))
    bot.send_message(message.chat.id,
                     text=f'Привет, {message.from_user.first_name}, я бот, помогающий отслеживать прогресс от похудения и тренировок',
                     reply_markup=markup)

@bot.message_handler(commands=['add'])
def add (message):

    data = []
    chat_id = message.chat.id
    add_support(message, 0)
    for i in list(dicti.values()):
        data.append(i[1])
    sheet = client.open(f'{chat_id}').sheet1
    sheet.append_row(data)
    print(data)


def add_support (message, index):
    chat_id = message.chat.id
    bot.register_next_step_handler_by_chat_id(chat_id, get_tada,  index)

def get_tada(message, index):
    chat_id = message.chat.id
    if index < 10:
        bot.send_message(chat_id, f'Введите {list(dicti.keys())[index]} в {list(dicti.values())[index][0]}')
        list(dicti.values())[index][1] = message.text
        print(message.text)
        add_support(message, index + 1)

bot.polling(none_stop=True, interval=0)