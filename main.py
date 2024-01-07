import telebot
import schedule
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import helper as h
from matplotlib import pyplot as plt

# Токен вашего Telegram-бота
BOT_TOKEN = '6390329177:AAGDCqaBc3dsqJmzGlOKgf8j3_ZjxANt4nA'

# ID таблицы
SPREEDSHEET_URL = 'https://docs.google.com/spreadsheets/d/1kcs30haX6RioXmzNyvyeCAODYgx5lq53EhL7qxOagzE/edit#gid=0'

# ID пользователя, которому нужно отправлять напоминание
USER_ID = '128687811'
USER_ID_2 = '314165610'

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('loseweighttrackbot-d7bf5bfe3d2a.json', scope)
client = gspread.authorize(creds)
worksheet = client.open_by_url(SPREEDSHEET_URL).sheet1

dict = {'Дата': '', 'Вес; кг': "", "Правая Ляха; см": "", "Левая Ляха; см": "", "Правая бицуха; см": "",
        "Левая бицуха; см": "", "Правая икра; см": "", "Левая Икра; см": "", "Шея; см": "", "Талия; см": "",
        "ИМТ; %": "", "До цели осталось; кг": "", "Процент жира; %": ""}

params = ''

for i in dict:
    params += i + '\n'


@bot.message_handler(commands=['start'])
def start(message):
    # bot.send_message(message.chat.id, f'Напишите /add, чтобы добавить данные в таблицу\n Напишите /view, чтобы посмотреть данные в определённую дату\n Напишите /plot, чтобы посмотреть график определённого показателя от времени (Пока не работает)')
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
def add(message):
    bot.send_message(message.chat.id,
                     'Введите данные в таком виде \nDATA \nдата - dd.mm.yy \nвес - кг \nправая ляха - см \nлевая ляха - см \nправая бицуха - см \nлевая бицуха - см \nправая икра - см \nлевая икра - см \nшея - см \nталия - см \n ЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')

@bot.message_handler(commands=['view'])
def view(message):
    bot.send_message(message.chat.id,
                     'Введите дату в формате dd.mm.yy, в которую хотите узнать показатели. Начните сообщение со слова TIME \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')

@bot.message_handler(commands=['plot'])
def plot(message):
    bot.send_message(message.chat.id,
                     'Введите показатель, график которого вы хотите построить, а также даты начала и конца в формате dd.mm.yy. Начните сообщение со слова PLOT \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
    bot.send_message(message.chat.id, f'Вот параметры, график которых я могу построить \n{params[5:]}')

@bot.message_handler(commands=['plot_other'])
def plot(message):
    bot.send_message(message.chat.id,
                     'Введите показатель, график которого вы хотите построить, а также даты начала и конца в формате dd.mm.yy. Начните сообщение со слова PLOT \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
    bot.send_message(message.chat.id, f'Вот параметры, график которых я могу построить \n{params[5:]}')

@bot.message_handler(commands=['view_other'])
def view(message):
    bot.send_message(message.chat.id,
                     'Введите дату в формате dd.mm.yy, в которую хотите узнать показатели. Начните сообщение со слова OTHER_TIME \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '/add':
        bot.send_message(call.message.chat.id,
                         'Введите данные в такой последовательности (только значения) \nDATA \nдата - dd.mm.yy \nвес - кг \nправая ляха - см \nлевая ляха - см \nправая бицуха - см \nлевая бицуха - см \nправая икра - см \nлевая икра - см \nшея - см \nталия - см \n ЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
    elif call.data == '/view':
        bot.send_message(call.message.chat.id,
                         'Введите дату в формате dd.mm.yy, в которую хотите узнать показатели. Начните сообщение со слова TIME \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
    elif call.data == '/plot':
        bot.send_message(call.message.chat.id,
                         'Введите показатель, график которого вы хотите построить, а также даты начала и конца в формате dd.mm.yy. Начните сообщение со слова PLOT \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
        bot.send_message(call.message.chat.id, f'Вот параметры, график которых я могу построить \n{params[5:]}')
    elif call.data == '/view_other':
        bot.send_message(call.message.chat.id,
                         'Введите дату в формате dd.mm.yy, в которую хотите узнать показатели. Начните сообщение со слова OTHER_TIME \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
    elif call.data == '/plot_other':
        bot.send_message(call.message.chat.id,
                         'Введите показатель, график которого вы хотите построить, а также даты начала и конца в формате dd.mm.yy. Начните сообщение со слова OTHER_PLOT \nЧЕРЕЗ ЗАПЯТУЮ В ОДНУ СТРОЧКУ')
        bot.send_message(call.message.chat.id, f'Вот параметры, график которых я могу построить \n{params[5:]}')

@bot.message_handler(content_types='text')
def handle_message(message):
    if message.text.startswith('DATA'):
        try:
            string = message.text.split(', ')[1:]
            date = string[0].split('.')
            row_index = int(date[0]) - 2

            h.add_data(message, worksheet, row_index, string, bot)
            h.add_data(message, worksheet, row_index, string, bot)

            bot.send_message(message.chat.id, 'Ваши данные успешно внесены в таблицу')
        except Exception as e:
            bot.send_message(message.chat.id, 'Перепроверьте ввод данных')

    elif message.text.startswith('TIME'):
        try:
            string = message.text.split(', ')[1:]
            date = int(string[0].split('.')[0])
            row_index = date - 2
            response = ''

            name = ''

            if message.chat.id == 128687811:
                name = 'Юра'
            elif message.chat.id == 314165610:
                name = 'Сеня'

            h.load_data(message, worksheet, row_index, dict, bot)

            response += name + '\n'


            for i in dict:
                item = f'{i}: {dict[i]}\n'
                response += item

            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, 'Ключевые слова и данные должны разделяться запятыми')

    elif message.text.startswith('PLOT'):
        try:
            string = message.text.split(', ')[1:]
            date_start = int(string[1].split('.')[0]) - 2
            date_end = int(string[2].split('.')[0]) - 2
            param = string[0]

            name = ''

            if message.chat.id == 128687811:
                name = 'Юра'
            elif message.chat.id == 314165610:
                name = 'Сеня'

            x = []
            y = []

            for i in range(date_start, date_end):
                h.load_data(message, worksheet, i, dict, bot)
                y.append(float(dict[param].replace(',', '.')))
                x.append(dict['Дата'])

            fig = plt.figure(figsize=(12, 8), dpi=500)
            plt.scatter(x, y, label=f'{param}, {name}')
            plt.xlabel('Дата')
            plt.ylabel(param)
            plt.title(f'{param} от времени')
            plt.grid()
            plt.legend()
            fig.savefig('plot.png')
            bot.send_photo(photo=open('plot.png', 'rb'), chat_id=message.chat.id, caption="Ваш график")
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id,
                             'Проверьте правильность ввода даты и параметра. Напоминаю, вводить надо PLOT, параметр (вместе с единицей измерения), дата начала, дата конца (не включительно)')

    elif message.text.startswith('OTHER_PLOT'):
        try:
            string = message.text.split(', ')[1:]
            date_start = int(string[1].split('.')[0]) - 2
            date_end = int(string[2].split('.')[0]) - 2
            param = string[0]

            name = ''

            if message.chat.id == 314165610:
                name = 'Юра'
            elif message.chat.id == 128687811:
                name = 'Сеня'

            x = []
            y = []

            for i in range(date_start, date_end):
                h.load_other_data(message, worksheet, i, dict, bot)
                y.append(float(dict[param].replace(',', '.')))
                x.append(dict['Дата'])

            fig = plt.figure(figsize=(12, 8), dpi=500)
            plt.scatter(x, y, label=f'{param}, {name}')
            plt.xlabel('Дата')
            plt.ylabel(param)
            plt.title(f'{param} от времени')
            plt.grid()
            plt.legend()
            fig.savefig('plot.png')
            bot.send_photo(photo=open('plot.png', 'rb'), chat_id=message.chat.id, caption="Ваш график")
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id,
                             'Проверьте правильность ввода даты и параметра. Напоминаю, вводить надо PLOT, параметр (вместе с единицей измерения), дата начала, дата конца (не включительно)')

    elif message.text.startswith('OTHER_TIME'):
        try:
            string = message.text.split(', ')[1:]
            date = int(string[0].split('.')[0])
            row_index = date - 2
            response = ''

            name = ''

            if message.chat.id == 314165610:
                name = 'Юра'
            elif message.chat.id == 128687811:
                name = 'Сеня'

            h.load_other_data(message, worksheet, row_index, dict, bot)

            response += name + '\n'

            for i in dict:
                item = f'{i}: {dict[i]}\n'
                response += item

            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, 'Ключевые слова и данные должны разделяться запятыми')

    else:
        bot.send_message(message.chat.id, 'Напишите /start')


# Функция для отправки ежедневного напоминания
def send_daily_reminder(User_id):
    message = "Заполни таблицу. Для этого введи /add"
    bot.send_message(User_id, message)


# Планирование отправки ежедневного напоминания
schedule.every().day.at("10:00").do(send_daily_reminder, USER_ID)
schedule.every().day.at("13:00").do(send_daily_reminder, USER_ID_2)


# Функция для запуска планировщика
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Запуск планировщика в отдельном потоке
    import threading

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Запуск Telegram-бота
    bot.polling(non_stop=True)
