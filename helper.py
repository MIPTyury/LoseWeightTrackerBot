import numpy as np


def load_data(message, worksheet, row_index, dict, bot):
        if message.chat.id == 128687811:
            data = list(worksheet.get(f'A{row_index}:U{row_index}'))[0]
            data += list(worksheet.get(f'X{row_index}:AA{row_index}'))[0]
            data = data[0:len(data):2]

            for i in range(len(list(dict.keys()))):
                keys = list(dict.keys())
                dict[keys[i]] = data[i]

        elif message.chat.id == 314165610:
            data = list(worksheet.get(f'A{row_index}:U{row_index}'))[0]
            data += list(worksheet.get(f'X{row_index}:AA{row_index}'))[0]
            data[1: len(data) // 2] = data[1:len(data):2]

            for i in range(len(list(dict.keys()))):
                keys = list(dict.keys())
                dict[keys[i]] = data[i]

def load_other_data(message, worksheet, row_index, dict, bot):
        if message.chat.id == 314165610:
            data = list(worksheet.get(f'A{row_index}:U{row_index}'))[0]
            data += list(worksheet.get(f'X{row_index}:AA{row_index}'))[0]
            data = data[0:len(data):2]

            for i in range(len(list(dict.keys()))):
                keys = list(dict.keys())
                dict[keys[i]] = data[i]

        elif message.chat.id == 128687811:
            data = list(worksheet.get(f'A{row_index}:U{row_index}'))[0]
            data += list(worksheet.get(f'X{row_index}:AA{row_index}'))[0]
            data[1: len(data) // 2] = data[1:len(data):2]

            for i in range(len(list(dict.keys()))):
                keys = list(dict.keys())
                dict[keys[i]] = data[i]



def fat_percent_calc(string, height):
    fat_percent = 495 / (
                1.0324 - 0.19077 * np.log10(float(string[-1]) - float(string[-2])) + 0.15456 * np.log10(height))
    fat_percent -= 450
    fat_percent = round(fat_percent, 1)
    return fat_percent


def add_data(message, worksheet, row_index, string, bot):
    try:
        if message.chat.id == 128687811:
            worksheet.update_cell(row_index, 1, string[0])
            for i in range(2, 2 * len(string)):
                if i % 2 == 1:
                    worksheet.update_cell(row_index, i, string[int((i - 1) / 2)])
            worksheet.update_cell(row_index, 2 * len(string) + 1, float(string[1]) / 1.73 / 1.73)
            worksheet.update_cell(row_index, 2 * len(string) + 5, float(string[1]) - 67)
            worksheet.update_cell(row_index, 2 * len(string) + 7, fat_percent_calc(string, 173))

        elif message.chat.id == 314165610:
            worksheet.update_cell(row_index, 1, string[0])
            for i in range(1, 2 * len(string)):
                if i % 2 == 0:
                    worksheet.update_cell(row_index, i, string[int((i + 1) / 2)])
            worksheet.update_cell(row_index, 2 * len(string), float(string[1]) / 1.83 / 1.83)
            worksheet.update_cell(row_index, 2 * len(string) + 4, float(string[1]) - 74)
            worksheet.update_cell(row_index, 2 * len(string) + 6, fat_percent_calc(string, 183))
    except Exception as e:
        bot.send_message(message.chat.id, "Проверьте правильность ввода данных")
