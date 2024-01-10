import datetime

import telebot
import schedule
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import helper as h
from matplotlib import pyplot as plt

# Токен вашего Telegram-бота
BOT_TOKEN = '6390329177:AAGDCqaBc3dsqJmzGlOKgf8j3_ZjxANt4nA' #основа
#BOT_TOKEN = '6523054368:AAEB4mPGXMHcygOCmxUBxxujtQ1MPCZNwQM' #юра
#BOT_TOKEN = '6939782498:AAG3ONAuKGlBHsUT-Wd1g-q_pBmDzz9eyB0' #сеня

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('loseweighttrackbot-d7bf5bfe3d2a.json', scope)
client = gspread.authorize(creds)

dicti = {'Дата':["", 0], 'Вес': ["кг", 0],'Правая ляха': ["см", 0],'Левая ляха': ["см", 0], 'Правая бицуха': ["см", 0],
         'Левая бицуха': ["см", 0], 'Правая икра': ["см", 0], 'Левая икра': ["см", 0], 'Шея': ["см", 0],
         'Талия': ["см", 0], 'Желаемый вес': ["кг", 0], 'Рост': ["см", 0], 'ИМТ': ["кг/м^2", 0],
         'Осталось до цели': ["кг", 0], 'Процент жира': ["%", 0]}

height = 173

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    name = message.from_user.first_name

    try:
        sheet = client.open(f'{chat_id}').sheet1
        bot.send_message(chat_id, 'ваша таблица найдена')
        # client.open(f'{chat_id}').share('yurafed03@gmail.com', perm_type='user', role='writer')
    except Exception as e:
        sheet = client.create(f'{chat_id}').sheet1
        sheet.append_row(list(dicti.keys()))
        bot.send_message(chat_id, 'создана таблица')

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Добавить данные', callback_data='/add'))
    markup.add(telebot.types.InlineKeyboardButton('Посмотреть данные (свои или друга)', callback_data='/view'))
    markup.add(telebot.types.InlineKeyboardButton('Построить график (свой или друга)', callback_data='/plot'))
    markup.add(telebot.types.InlineKeyboardButton('Удалить последнюю записанную строку (удаляет сразу, подтверждения действия не предусмотрено)', callback_data='/remove_last'))
    markup.add(telebot.types.InlineKeyboardButton('Удалить таблицу (удаляет сразу, подтверждения действия не предусмотрено)', callback_data='/delete_table'))

    if (message.chat.id == 128687811 or message.chat.id == 314165610):
        markup.add(telebot.types.InlineKeyboardButton('Посмотреть список таблиц и их создателей (функция админов)', callback_data='/check_tables'))

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
    elif call.data == '/plot':
        plot(call.message)
    elif call.data == '/check_tables':
        check_tables(call.message)

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
        waist = float(list(dicti.values())[9][1])
        categ = list(dicti.keys())[14]
        dicti[categ][1] = round(495 / (1.0324 - 0.19077 * np.log10(waist - neck) + 0.15456 * np.log10(float(list(dicti.values())[11][1]))) - 450, 1)

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

@bot.message_handler(commands=['view'])
def view(message):
    chat_id = message.chat.id
    try:
        client.open(f'{chat_id}').sheet1
        insert_id(message)
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

def insert_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Введите id друга или 0, если хотите посмотреть свои данные')
    bot.register_next_step_handler_by_chat_id(chat_id, view_support_by_id)

def view_support_by_id(message):
    chat_id = message.chat.id
    if message.text == '0':
        id = chat_id
    else:
        id = message.text
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, get_data_by_id, id)

def get_data_by_id(message, id):

    data = collect_data(message.text, id)

    if data == -1:
        bot.send_message(message.chat.id, f'на дату {message.text} нет данных')
    else:
        response = ''
        for i in range(len(list(dicti.keys()))):
            keys = list(dicti.keys())
            values = list(dicti.values())
            item = f'{keys[i]}: {data[i]} {values[i][0]}\n'
            response += item
        print(response)
        bot.send_message(message.chat.id, response)

def collect_data(date, id):
    sheet = client.open(f'{id}').sheet1
    dates = sheet.col_values(1)
    index = -1
    for i in range(len(dates)):
        if dates[i] == date:
            index = i
    if index == -1:
        return -1

    data = sheet.row_values(index + 1)

    return data

@bot.message_handler(commands=['plot'])
def plot(message):
    insert_plot_id(message)


def insert_plot_id(message):
    bot.send_message(message.chat.id, f'Введите id друга или 0, если хотите посмотреть свои данные')
    bot.register_next_step_handler_by_chat_id(message.chat.id, insert_parametr)


def insert_parametr(message):
    if message.text == '0':
        id = message.chat.id
    else:
        id = message.text
    bot.send_message(message.chat.id, f'Введите параметр, график которого вы хотите построить')
    titels = ''
    for i in list(dicti.keys())[1:]:
        if i != 'Желаемый вес':
            titels += i + '\n'
    bot.send_message(message.chat.id, titels)
    bot.register_next_step_handler_by_chat_id(message.chat.id, insert_start_date, id)

def insert_start_date(message, id):
    param = message.text
    bot.send_message(message.chat.id, f'Введите дату начала')
    bot.register_next_step_handler_by_chat_id(message.chat.id, insert_end_date, id, param)

def insert_end_date(message, id, param):
    start_date = list(map(int, reversed(message.text.split('.'))))
    start_date = datetime.date(start_date[0], start_date[1], start_date[2])
    bot.send_message(message.chat.id, f'Введите дату кончала')
    bot.register_next_step_handler_by_chat_id(message.chat.id, plot_collector, id, param, start_date)

def plot_collector(message, id, param, start_date):
    date = start_date
    a = collect_data(date, id)
    data = []
    date_ls = []
    end_date = list(map(int, reversed(message.text.split('.'))))
    end_date = datetime.date(end_date[0], end_date[1], end_date[2])
    interval = (end_date - start_date).days
    for i in range(interval):
        date = date.strftime('%d.%m.%Y')
        date_ls.append(date)
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        date += datetime.timedelta(days= 1)
    for i in date_ls:
        data.append(collect_data(i, id)[find_index(param, dicti)])
    plot_builder(message, date_ls, list(map(float, data)), param, id)

def plot_builder(message, x, y, param, id):
    fig = plt.figure(figsize=(12, 8), dpi=400)
    plt.scatter(x, y, label=f'{param}, {bot.get_chat(id).first_name}')
    plt.xlabel('дата')
    plt.ylabel(f'{param}, {dicti[param][0]}')
    plt.title(f'{param} от времени для {bot.get_chat(id).first_name}')
    plt.legend()
    plt.grid()
    fig.savefig('plot.png')
    bot.send_photo(message.chat.id, photo=open('plot.png', 'rb'), caption='ваш график')

def find_index(param, dict):
    index = 1
    for i in range(len(list(dict.keys()))):
        if list(dict.keys())[i] == param:
            index = i
    return index




#Служебная команда только для админа
@bot.message_handler(commands=['check_tables'])
def check_tables(message):
    chat_id = message.chat.id
    if chat_id == 128687811 or chat_id == 314165610:
        tables = []
        for i in client.openall():
            tables.append({'title': i.title, 'id': i.id, 'name':bot.get_chat(int(i.title)).first_name, 'link': '@' + str(bot.get_chat(int(i.title)).username)})

        response = ''

        for i in tables:
            for j in i:
                response += j + ': ' + i[j] + '\n'
            response += '\n'

        bot.send_message(chat_id, response)

bot.polling(none_stop=True, interval=0)