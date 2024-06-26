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
BOT_TOKEN = '6390329177:AAGDCqaBc3dsqJmzGlOKgf8j3_ZjxANt4nA'  # основа
# BOT_TOKEN = '6523054368:AAEB4mPGXMHcygOCmxUBxxujtQ1MPCZNwQM' # юра
# BOT_TOKEN = '6939782498:AAG3ONAuKGlBHsUT-Wd1g-q_pBmDzz9eyB0' # сеня

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('loseweighttrackbot-d7bf5bfe3d2a.json', scope)
client = gspread.authorize(creds)

dicti = {'Дата': ["", 0], 'Вес': ["кг", 0], 'Правая ляха': ["см", 0], 'Левая ляха': ["см", 0],
         'Правая бицуха': ["см", 0],
         'Левая бицуха': ["см", 0], 'Правая икра': ["см", 0], 'Левая икра': ["см", 0], 'Шея': ["см", 0],
         'Талия': ["см", 0], 'Желаемый вес': ["кг", 0], 'Рост': ["см", 0], 'ИМТ': ["кг/м^2", 0],
         'Осталось до цели': ["кг", 0], 'Процент жира': ["%", 0]}

is_ready = True
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
    markup.add(telebot.types.InlineKeyboardButton(
        'Удалить последнюю записанную строку (удаляет сразу, подтверждения действия не предусмотрено)',
        callback_data='/remove_last'))
    markup.add(
        telebot.types.InlineKeyboardButton('Удалить таблицу (удаляет сразу, подтверждения действия не предусмотрено)',
                                           callback_data='/delete_table'))

    if (message.chat.id == 128687811 or message.chat.id == 314165610):
        markup.add(telebot.types.InlineKeyboardButton('Посмотреть список таблиц и их создателей (функция админов)',
                                                      callback_data='/check_tables'))

    bot.send_message(message.chat.id,
                     text=f'Привет, {name}, я бот, помогающий отслеживать прогресс от похудения и тренировок. Для описания всех команд напишите /help',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '/add_ext' and is_ready:
        add_ext(call.message)
    elif call.data == '/view' and is_ready:
        view(call.message)
    elif call.data == '/delete_table' and is_ready:
        delete_table(call.message)
    elif call.data == '/remove_last' and is_ready:
        remove_last(call.message)
    elif call.data == '/plot' and is_ready:
        plot(call.message)
    elif call.data == '/check_tables' and is_ready:
        check_tables(call.message)

@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    text = '/start - старт бота\n/help - описание всех функций\n/add_ext - добавить данные (если в первый раз добавляете данные, используйте именно её)\n/add - добавление данных (работает начиная со второго дня, добавляет только дату и вес\n/plot - строит график указанного параметра от времени\n/view - просмотреть данные (свои или друга)\n/view_last - просмотреть последнюю запись\n/view_first - просмотреть первую запись\n/remove_last - удаляет последнюю запись (сразу же, при нажатии)\n/delete_table - удаляет таблицу (сразу же, при нажатии)\n'
    bot.send_message(chat_id, text)


def parser(data):
    response = ''
    for i in range(len(list(dicti.keys()))):
        keys = list(dicti.keys())
        values = list(dicti.values())
        item = f'{keys[i]}: {data[i]} {values[i][0]}\n'
        response += item
    return(response)

def check_date_type(message):
    try:
        # Попытка преобразовать строку в дату
        date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
        print("Строка содержит действительную дату:", date)
        return True
    except ValueError:
        print("Строка НЕ содержит действительную дату")
        return False

def get_data(id, param):
    sheet = client.open(f'{id}').sheet1
    data = sheet.get_all_values()
    index = find_index(param, dicti)
    dates = []
    for i in range(0, len(data)):
        dates.append(data[i][0])

    dict_data = {}
    for i in range(1, len(dates)):
        dict_data[dates[i]] = data[i][index]
    return dict_data

@bot.message_handler(commands=['add_ext'])
def add_ext(message):
    global is_ready
    is_ready = False
    chat_id = message.chat.id
    try:
        client.open(f'{chat_id}').sheet1
        add_ext_support(message, 0)
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

def add_ext_support(message, index):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[index]} в {list(dicti.values())[index][0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, set_data_ext, index)

def set_data_ext(message, index):
    chat_id = message.chat.id
    if index != -1:
        categ = list(dicti.keys())[index]
        if index == 0:
                if not check_date_type(message):
                    bot.send_message(chat_id, 'дату необходимо вводить в формате дд.мм.гггг')
                    bot.register_next_step_handler_by_chat_id(chat_id, set_data, index)
                    return
                else:
                    dicti['Дата'][1] = message.text
        elif index > 0 and index <= 11:
            if str(message.text).replace('.', '').isdigit() and len(str(message.text).replace('.', '')) < 5:
                dicti[categ][1] = message.text
            else:
                bot.send_message(chat_id, "Вводить надо числа с разделителем в виде точки")
                bot.register_next_step_handler_by_chat_id(chat_id, set_data, index)
                return

    if index < 11 and index != -1:
        add_ext_support(message, index + 1)
    elif index == 11:
        categ = list(dicti.keys())[12]
        if float(list(dicti.values())[11][1]) != 0:
            dicti[categ][1] = round(float(list(dicti.values())[1][1]) / ((float(list(dicti.values())[11][1]) / 100) ** 2),
                                1)

        neck = float(list(dicti.values())[8][1])
        waist = float(list(dicti.values())[9][1])
        categ = list(dicti.keys())[14]
        if waist - neck != 0 and float(list(dicti.values())[11][1]) != 0:
            dicti[categ][1] = round(495 / (1.0324 - 0.19077 * np.log10(waist - neck) + 0.15456 * np.log10(
                float(list(dicti.values())[11][1]))) - 450, 1)

        categ = list(dicti.keys())[13]
        dicti[categ][1] = round(float(list(dicti.values())[1][1]) - float(list(dicti.values())[10][1]), 1)

        set_data_ext(message, -1)
    else:
        data = []
        for i in dicti.values():
            data.append(i[1])
        sheet = client.open(f'{chat_id}').sheet1
        sheet.append_row(data)
        bot.send_message(chat_id, 'Данные введены')
        global is_ready
        is_ready = True

@bot.message_handler(commands=['add'])
def add(message):
    global is_ready
    is_ready = False
    chat_id = message.chat.id
    try:
        sheet = client.open(f'{chat_id}').sheet1
        test = sheet.get_all_values()
        pivot_data = []
        if len(test) != 1:
            pivot_data = collect_data(list(sheet.row_values(len(test)))[0], chat_id)
            print('check----', pivot_data)
            add_support(message, 0, pivot_data)
        else:
            bot.send_message(message.chat.id, 'У вас нет предыдущих данных \nЗаполните, используя /add_ext')
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

def add_support(message, index, data):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[index]} в {list(dicti.values())[index][0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, set_data, index, data)

def set_data(message, index, data):
    chat_id = message.chat.id
    if index != -1:
        if index == 0:
                if not check_date_type(message):
                    bot.send_message(chat_id, 'дату необходимо вводить в формате дд.мм.гггг')
                    bot.register_next_step_handler_by_chat_id(chat_id, set_data, index)
                    return
                else:
                    data[0] = message.text

        elif index == 1:
            if str(message.text).replace('.', '').isdigit() and len(str(message.text).replace('.', '')) < 5:
                data[1] = message.text
            else:
                bot.send_message(chat_id, "Вводить надо числа с разделителем в виде точки")
                bot.register_next_step_handler_by_chat_id(chat_id, set_data, index)
                return

    if index < 1 and index != -1:
        add_support(message, index + 1, data)
    elif index == 1:
        if float(data[11]) != 0:
            data[12] = round(float(data[1]) / ((float(data[11]) / 100) ** 2),
                                1)

        data[13] = round(float(data[1]) - float(data[10]), 1)

        set_data(message, -1, data)
    else:
        sheet = client.open(f'{chat_id}').sheet1
        sheet.append_row(data)
        bot.send_message(chat_id, 'Данные введены')
        global is_ready
        is_ready= True

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

@bot.message_handler(commands=['view_last'])
def view_last(message):
    chat_id = message.chat.id
    try:
        sheet = client.open(f'{chat_id}').sheet1
        try:
            test = sheet.get_all_values()
            print(len(test))
            if len(test) != 1:
                data = collect_data(list(sheet.row_values(len(test)))[0], chat_id)
                print(data)
                bot.send_message(chat_id, parser(data))
            else:
                bot.send_message(chat_id, 'хуй')
        except:
            bot.send_message(chat_id, 'В таблице нет записей, вы можете их добавить с помощью /add')
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')

@bot.message_handler(commands=['view_first'])
def view_first(message):
    chat_id = message.chat.id
    try:
        sheet = client.open(f'{chat_id}').sheet1
        try:
            test = sheet.get_all_values()
            print(len(test))
            if len(test) != 1:
                data = collect_data(list(sheet.row_values(2))[0], chat_id)
                print(data)
                bot.send_message(chat_id, parser(data))
            else:
                bot.send_message(chat_id, 'хуй')
        except:
            bot.send_message(chat_id, 'В таблице нет записей, вы можете их добавить с помощью /add')
    except:
        bot.send_message(chat_id, 'Для вас ещё нет таблицы, напишите /start')
@bot.message_handler(commands=['view'])
def view(message):
    global is_ready
    is_ready = False
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
        try:
            sheet = client.open(f'{id}').sheet1
            check_data = sheet.get_all_values()
            if len(check_data) == 1:
                bot.send_message(chat_id, "Пользователь не ввел никакие данные, для добавления есть команда /add")
        except Exception as e:
            bot.send_message(chat_id, f'Для пользователя с id: {id} нет таблицы, попробуйте ввести другой')
            bot.register_next_step_handler_by_chat_id(chat_id, view_support_by_id)
            return
    bot.send_message(chat_id, f'Введите {list(dicti.keys())[0]}')
    bot.register_next_step_handler_by_chat_id(chat_id, get_data_by_id, id)

def get_data_by_id(message, id):
    data = collect_data(message.text, id)

    if data == -1:
        try:
            # Попытка преобразовать строку в дату
            date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
            print("Строка содержит действительную дату:", date)
            dicti["Дата"][1] = message.text
        except ValueError:
            print("Строка НЕ содержит действительную дату")
            bot.send_message(message.chat.id, "Напишите дату в формате дд.мм.гггг")
            bot.register_next_step_handler_by_chat_id(message.chat.id, get_data_by_id, id)
            return
        bot.send_message(message.chat.id, f'на дату {message.text} нет данных, попробуйте другую')
        bot.register_next_step_handler_by_chat_id(message.chat.id, get_data_by_id, id)
        return
    else:
        response = parser(data)
        bot.send_message(message.chat.id, response)
        global is_ready
        is_ready = True

def collect_data(date, id):
    try:
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
    except Exception as e:
        return -2

@bot.message_handler(commands=['predict'])
def predict(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите дату, до которой вы хотите посмотреть прогноз')
    bot.register_next_step_handler_by_chat_id(chat_id, predictor_plot)

def predictor_plot(message):
    chat_id = message.chat.id
    sheet = client.open(f'{chat_id}').sheet1
    test = sheet.get_all_values()
    dates = []
    weight = []
    for i in range(1, len(test)):
        dates.append(test[i][0])
        weight.append(round(float(test[i][1]), 2))
    delta = (datetime.datetime.strptime(dates[-1], '%d.%m.%Y') - datetime.datetime.strptime(dates[1], '%d.%m.%Y')).days

    x = np.arange(1, delta + 3)
    y = weight
    print('lens', len(x), len(y))
    print(x, y, sep='\n')
    coef = np.polyfit(x[-15:-1], y[-15:-1], 1)
    y_opt = coef[0] * x[-15:-1] + coef[1]
    print(coef)
    for i in range(len(y_opt)):
        y_opt[i] = round(y_opt[i], 2)
    if check_date_type(message) == False:
        bot.send_message(message.chat.id, 'Дату введите правильно дд.мм.гггг')
        bot.register_next_step_handler_by_chat_id(chat_id, predictor_plot)
    else:
        new_delta = (datetime.datetime.strptime(message.text, '%d.%m.%Y') - datetime.datetime.strptime(dates[-1], '%d.%m.%Y')).days
        x_opt = np.arange(1, delta + 3 + new_delta)
        y_pred = coef[0]*x_opt + coef[1]
        for i in range(len(y_pred)):
            y_pred[i] = round(y_pred[i], 2)

        for i in range(new_delta):
            dates.append((datetime.datetime.strptime(dates[-1], '%d.%m.%Y') + datetime.timedelta(days=1)).strftime('%d.%m.%Y'))

        print(y_pred, dates, sep='\n')
        output = 0
        for i in range(len(x_opt)):
            if dates[i] == message.text:
                output = y_pred[i]

        bot.send_message(message.chat.id, f'{message.text} ожидается, что будет {output} Кг')


@bot.message_handler(commands=['plot'])
def plot(message):
    global is_ready
    is_ready = False
    insert_plot_id(message)

def insert_plot_id(message):
    bot.send_message(message.chat.id, f'Введите id друга или 0, если хотите посмотреть свои данные')
    bot.register_next_step_handler_by_chat_id(message.chat.id, insert_parametr)

def insert_parametr(message):
    if message.text == '0':
        id = message.chat.id
    else:
        id = message.text
        try:
            client.open(f'{id}').sheet1
        except Exception as e:
            bot.send_message(message.chat.id, f'Для данного пользователя нет таблицы, попробуйте ещё раз')
            bot.register_next_step_handler_by_chat_id(message.chat.id, insert_parametr)
            return
    bot.send_message(message.chat.id, f'Введите параметр, график которого вы хотите построить')
    titels = ''
    for i in list(dicti.keys())[1:]:
        if i != 'Желаемый вес':
            titels += i + '\n'
    bot.send_message(message.chat.id, titels)
    bot.register_next_step_handler_by_chat_id(message.chat.id, insert_start_date, id)

def insert_start_date(message, id):
    param = message.text
    if param not in dicti.keys():
        bot.send_message(message.chat.id, f'Такого параметра нет, введите ещё раз')
        bot.register_next_step_handler_by_chat_id(message.chat.id, insert_start_date, id)
    else:
        bot.send_message(message.chat.id, f'Введите дату начала')
        bot.register_next_step_handler_by_chat_id(message.chat.id, insert_end_date, id, param)

def insert_end_date(message, id, param):
    if check_date_type(message):
        start_date = message.text
        bot.send_message(message.chat.id, f'Введите дату кончала')
        bot.register_next_step_handler_by_chat_id(message.chat.id, plot_collector, id, param, start_date)
    else:
        bot.send_message(message.chat.id, "Напишите дату в формате дд.мм.гггг")
        bot.register_next_step_handler_by_chat_id(message.chat.id, insert_end_date, id, param)

def plot_collector(message, id, param, start_date):
    date = start_date
    a = collect_data(date, id)
    if a == -2:
        return
    data = []
    date_ls = []
    if check_date_type(message):
        end_date = message.text
        data = get_data(id, param)
        x = list(data.keys())
        y = list(map(float, list(data.values())))
        if (len(x) == 0 or len(y) == 0):
            bot.send_message(message.chat.id, 'Вы не вводили данные, пожалуйста введите их с помощью команды /add')
            return
        try:
            bot.send_message(message.chat.id, f'График строится. Подождите немного')
            start_index = x.index(start_date)
            end_index = x.index(end_date) + 1
        except Exception as e:
            start_index = 0
            end_index = len(data)

        x = x[start_index:end_index]
        y = y[start_index:end_index]
        plot_builder(message, x, y, param, id)
    else:
        bot.send_message(message.chat.id, "Напишите дату в формате дд.мм.гггг")
        bot.register_next_step_handler_by_chat_id(message.chat.id, plot_collector, id, param, start_date)

def plot_builder(message, x, y, param, id):
    fig = plt.figure(figsize=(12, 8), dpi=400)
    plt.scatter(x, y, label=f'{param}, {bot.get_chat(id).first_name}')
    plt.xticks(rotation=45)
    plt.ylabel(f'{param}, {dicti[param][0]}')
    plt.title(f'{param} от времени для {bot.get_chat(id).first_name}')
    plt.legend()
    plt.grid()
    fig.savefig('plot.png')
    bot.send_photo(message.chat.id, photo=open('plot.png', 'rb'), caption='ваш график')
    global is_ready
    is_ready = True

def find_index(param, dict):
    index = 1
    for i in range(len(list(dict.keys()))):
        if list(dict.keys())[i] == param:
            index = i
    return index

# Служебная команда только для админа
@bot.message_handler(commands=['check_tables'])
def check_tables(message):
    chat_id = message.chat.id
    if chat_id == 128687811 or chat_id == 314165610:
        tables = []
        for i in client.openall():
            tables.append({'title': i.title, 'id': i.id, 'name': bot.get_chat(int(i.title)).first_name,
                           'link': '@' + str(bot.get_chat(int(i.title)).username)})

        response = ''

        for i in tables:
            for j in i:
                response += j + ': ' + i[j] + '\n'
            response += '\n'

        with open('users.txt', 'w', encoding='utf-8') as file:
            file.writelines(response)
            
        bot.send_document(chat_id, document=open('users.txt', 'rb'))

bot.polling(none_stop=True, interval=0)
