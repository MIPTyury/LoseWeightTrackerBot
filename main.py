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
BOT_TOKEN = '6523054368:AAEB4mPGXMHcygOCmxUBxxujtQ1MPCZNwQM'

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('loseweighttrackbot-d7bf5bfe3d2a.json', scope)
client = gspread.authorize(creds)

dicti = {'Дата':["", 0], 'Вес': ["кг", 0],'Правая ляха': ["см", 0],'Левая ляха': ["см", 0], 'Правая бицуха': ["см", 0],
         'Левая бицуха': ["см", 0], 'Правая икра': ["см", 0], 'Левая икра': ["см", 0], 'Шея': ["см", 0],
         'Талия': ["см", 0], 'Желаемый вес': ["кг", 0], 'Рост': ["см", 0], 'ИМТ': [r"$кг/м^2$", 0],
         'Осталось до цели': ["кг", 0], 'Процент жира': ["%", 0]}

height = 173

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    name = message.from_user.first_name

    try:
        sheet = client.open(f'{chat_id}').sheet1
        bot.send_message(chat_id, 'ваша таблица найдена')
        client.open(f'{chat_id}').share('yurafed03@gmail.com', perm_type='user', role='writer')
    except Exception as e:
        sheet = client.create(f'{chat_id}').sheet1
        sheet.append_row(list(dicti.keys()))
        bot.send_message(chat_id, 'создана таблица')

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Добавить данные в таблицу', callback_data='/add'))
    markup.add(telebot.types.InlineKeyboardButton('Посмотреть данные таблицы', callback_data='/view'))
    markup.add(telebot.types.InlineKeyboardButton('Удалить таблицу', callback_data='/delete_table'))
    markup.add(telebot.types.InlineKeyboardButton('Удалить последнюю записанную строку', callback_data='/remove_last'))
    # markup.add(telebot.types.InlineKeyboardButton('Посмотреть данные таблицы другого человека (NA)', callback_data='/view_other'))
    # markup.add(telebot.types.InlineKeyboardButton('Построить график параметра (NA)', callback_data='/plot'))
    # markup.add(telebot.types.InlineKeyboardButton('Построить график параметра другого человека (NA)', callback_data='/plot_other'))
    bot.send_message(message.chat.id,
                     text=f'Привет, {name}, я бот, помогающий отслеживать прогресс от похудения и тренировок',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '/add':
        add(call.message)
    elif call.data == '/view':
        view(call.message)
    elif call.data == '/delete_table':
        delete_table(call.message)
    elif call.data == '/remove_last':
        remove_last(call.message)

@bot.message_handler(commands=['add'])
def add(message):
    chat_id = message.chat.id
    try:
        client.open(f'{chat_id}').sheet1
        add_support(message, 0)
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

def add_support(message, index):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[index]} в {list(dicti.values())[index][0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, set_data,  index)

def set_data(message, index):
    chat_id = message.chat.id
    if index != -1:
        categ = list(dicti.keys())[index]
        dicti[categ][1] = message.text

    if index < 11 and index != -1:
        add_support(message, index + 1)
    elif index == 11:
        categ = list(dicti.keys())[12]
        dicti[categ][1] = round(float(list(dicti.values())[1][1]) / ((float(list(dicti.values())[11][1]) / 100)**2), 1)

        neck = float(list(dicti.values())[8][1])
        tallia = float(list(dicti.values())[9][1])
        categ = list(dicti.keys())[14]
        dicti[categ][1] = round(495 / (1.0324 - 0.19077 * np.log10(tallia - neck) + 0.15456 * np.log10(float(list(dicti.values())[11][1]))) - 450, 1)

        categ = list(dicti.keys())[13]
        dicti[categ][1] = round(float(list(dicti.values())[1][1]) - float(list(dicti.values())[10][1]), 1)

        set_data(message, -1)
    else:
        data = []
        for i in dicti.values():
            data.append(i[1])
        sheet = client.open(f'{chat_id}').sheet1
        sheet.append_row(data)
        bot.send_message(chat_id, 'Данные введены')

@bot.message_handler(commands=['view'])
def view(message):
    chat_id = message.chat.id
    try:
        client.open(f'{chat_id}').sheet1
        view_support(message)
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

def view_support(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, get_data)

def get_data(message):
    chat_id = message.chat.id
    sheet = client.open(f'{chat_id}').sheet1
    dates = sheet.col_values(1)
    print(dates)
    index = -1
    for i in range(len(dates)):
        if dates[i] == message.text:
            index = i
    if index == -1:
        bot.send_message(chat_id, 'На эту дату в таблице нет записей. Вы можете добавить их с помощью команды /add')
        return

    data = sheet.row_values(index + 1)
    response = ''
    for i in range(len(list(dicti.keys()))):
        keys = list(dicti.keys())
        values = list(dicti.values())
        item = f'{keys[i]}: {data[i]} {values[i][0]}\n'
        response += item
    print(response)
    bot.send_message(chat_id, response)
@bot.message_handler(commands=['delete_table'])
def delete_table(message):
    chat_id = message.chat.id
    tables = []
    for i in client.openall():
        tables.append({'title': i.title, 'id': i.id})

    if len(tables) != 0:
        for i in tables:
            if i['title'] == str(chat_id):
                client.del_spreadsheet(i['id'])

        bot.send_message(message.chat.id, 'Удаление завершено')
    else:
        bot.send_message(chat_id, 'Нет таблиц для удаления')

@bot.message_handler(commands=['remove_last'])
def remove_last(message):
    chat_id = message.chat.id
    try:
        sheet = client.open(f'{chat_id}').sheet1
        try:
            test = sheet.get_all_values()
            sheet.delete_rows(len(test))
            bot.send_message(chat_id, 'Удалена последняя строка')
        except:
            bot.send_message(chat_id, 'В таблице нет записей, вы можете их добавить с помощью /add')
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')






#Служебная команда только для админа
@bot.message_handler(commands=['check_tables'])
def check_tables(message):
    chat_id = message.chat.id
    if chat_id == 128687811:
        tables = []
        for i in client.openall():
            tables.append({'title': i.title, 'id': i.id})
        print(tables)
        bot.send_message(chat_id, str(tables))

bot.polling(none_stop=True, interval=0)