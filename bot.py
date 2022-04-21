import time
from db_io import DataBase
import datetime
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import os
import sqlite3
import global_vars
from Config import *

version_bot = '1.0.1.3 (build v223)'

bot = telebot.TeleBot(BOT_TOKEN)

DB = DataBase()


def back(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Английский язык', 'Математика']])
    keyboard.add(*[types.KeyboardButton(name) for name in ['Русский язык', 'Физика']])
    keyboard.add(*[types.KeyboardButton(name) for name in ['История', 'Французский язык', 'Химия']])
    keyboard.add(*[types.KeyboardButton(name) for name in ['Домой🏠']])
    send = bot.send_message(message.from_user.id, "Выберите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(send, subject)


def parseBS(url, message, sendMes, start, end, condition="@", arr=[], permission=False):
    # arr = [ 10] 10 - max element in stack gdz
    try:
        if permission or int(message.text) in range(start, end + 1):
            # startTime = time.time()
            if not arr:
                sourceCode = requests.get(url).text
                soup = BeautifulSoup(sourceCode, "lxml")
                srx = soup.find_all("div", {"class": "with-overtask"})
                if condition == "@":
                    urls = [i.find("img")["src"] for i in srx]
                else:
                    urls = [i.find('img')['src'] for i in srx if condition in i.find('img')['alt']]
                downloadFile(urls, message, start="http:")
            else:
                print(url)
                for i in range(arr[0]):
                    try:
                        urlx = f"{url}{i}.jpg"
                        downloadFile([urlx], message)
                    except Exception as ex:
                        print(ex)
                        break
            if not permission:
                bot.send_message(message.from_user.id, f'{sendMes} {message.text}')
            # endTime = time.time()
            # bot.send_message(message.from_user.id, f'Ответ дан за {endTime - startTime:.5f} sec')      выключил отображение времени выполнения запроса
        else:
            bot.send_message(message.from_user.id, "Введите корректное значение номера.")
    except Exception as ex:
        bot.send_message(message.from_user.id, f"ERROR: {ex}")


def downloadFile(urls, message, start=""):
    for i in urls:
        try:
            p = requests.get(f"{start}{i}")
            if sendWritePhoto(message, "img.jpg", p.content) == "OK":
                continue
            break
        except Exception as ex:
            print(ex)


def sendWritePhoto(message, filename, data):
    try:
        with open(filename, "wb") as file:
            file.write(data)
            file.close()
        with open(filename, "rb") as f:
            bot.send_photo(message.from_user.id, photo=f)
        os.remove(filename)
        return "OK"
    except:
        return "ERROR"


@bot.message_handler(commands=['delete'])
def delete_from_bd(message):
    verdict = DB.delete(message.from_user.id)
    bot.send_message(message.from_user.id, verdict)


@bot.message_handler(commands=['list'])
def lis(message):
    send = os.listdir(path='.')
    bot.send_message(message.from_user.id, '\n'.join(send))


@bot.message_handler(commands=['help_admin'])
def help_admin(message):
    bot.send_message(message.from_user.id,
                     "Команды:\n/mail - отправка рассылки\n/upload - загрузка в бота базы данных\n/BaseData - база "
                     "данных и бекап на Google Drive\n/list - информация о файлах в директории бота")


@bot.message_handler(commands=['mail'])
def mail(message):
    if NAME_DB in os.listdir(path='.'):
        if message.from_user.username == USERNAME_ADMIN:
            request = 0
            try:
                mail_txt = str(message.text[6:])
            except Exception as ex:
                bot.send_message(996780194, ex)
            for line in DB.ALL_IDs_FROM_DB:
                try:
                    bot.send_message(line, mail_txt)
                    request = request + 1
                    time.sleep(0.5)
                    if request % 30 == 0:
                        time.sleep(1.5)
                        request = 0
                    bot.send_message(996780194, f'Сообщение отправлено пользователю с ID {line}')
                except:
                    print('ERROR - user blocked bot, pass')
                    continue
        else:
            print('bad')
    else:
        DB.upload_file()


@bot.message_handler(commands=['last_mail'])
def last_mail(message):
    if message.from_user.username == USERNAME_ADMIN:
        request = 0
        try:
            mail_txt = str(message.text[6:])
        except Exception as ex:
            bot.send_message(996780194, ex)
        for line in DB.ALL_IDs_FROM_DB:
            try:
                bot.send_message(line, mail_txt)
                request = request + 1
                time.sleep(0.5)
                if request % 30 == 0:
                    time.sleep(1.5)
                    request = 0
                bot.send_message(996780194, f'Сообщение отправлено пользователю с ID {line}')
            except:
                print('ERROR - user blocked bot, pass')
                continue
    else:
        print('bad')


@bot.message_handler(commands=['upload'])
def upload_file_handler(message):  # загрузка бд в директорию бота
    if message.from_user.id == USERNAME_ADMIN:
        DB.upload_file()
        bot.send_message(message.from_user.id, "Загрузка проведена успешно")


@bot.message_handler(commands=['ask_dz'])
def ask_home_work(message: telebot.types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Сказать ДЗ', callback_data='answer_on_hw'))
    bot.send_message(message.from_user.id, 'Скажите пожалуйста домашнее задание на завтра :-)', reply_markup=kb)
    if 'test' not in message.text:
        if message.from_user.username == USERNAME_ADMIN:
            request = 0
            for line in DB.ALL_IDs_FROM_DB:
                try:
                    bot.send_message(line, 'Скажите пожалуйста домашнее задание на завтра :-)', reply_markup=kb)
                    request = request + 1
                    time.sleep(0.5)
                    if request % 30 == 0:
                        time.sleep(1.5)
                        request = 0
                    bot.send_message(996780194, f'Сообщение отправлено пользователю с ID {line}')
                except:
                    print('ERROR - user blocked bot, pass')
                    continue
        else:
            print('bad')


@bot.message_handler(commands=['BaseData'])
def secur(message):  # бекап текущей версии бд на гугл диск и отправка ее администратору
    file_db = open(NAME_DB, 'rb')
    bot.send_document(message.chat.id, file_db)
    file_db.close()
    DB.backup()


@bot.message_handler(content_types=["text"])
@bot.message_handler(commands=['start'])
def first(message):
    try:
        if str(message.from_user.id) in DB.ALL_IDs_FROM_DB:
            key = types.ReplyKeyboardMarkup(True, False)
            key.row('Расписание', 'ГДЗ', 'Информация')
            send = bot.send_message(message.from_user.id, "Меню", reply_markup=key)
            bot.register_next_step_handler(send, menu)
        else:
            DB.add_user(message)
            bot.send_message(message.from_user.id, 'Вы добавлены в БД. Это разовая процедура. '
                                                   'Перезапустите бота командой /start или любым сообщением.')
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


def input_home_word(message):
    if message.text == 'Отмена':
        back(message)
    else:
        bot.send_message(CHAT_HOME_WORK,
                         f"Пользователь отправил ДЗ.\nUser ID: {message.from_user.id}\nUser Tag: @{message.from_user.username}\n\n{message.text}")
        with open('data/happy-cat-6.gif', 'rb') as gif:
            bot.send_video(message.from_user.id, gif, caption='Спасибо!!!')
        back(message)


def menu(message):
    if message.text == 'Расписание':
        img = open(NAME_OF_PIC_SCHED, 'rb')
        bot.send_photo(message.chat.id, photo=img)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Домой🏠']])
        send = bot.send_message(message.from_user.id, "Расписание на неделю", reply_markup=keyboard)
        bot.register_next_step_handler(send, subject)

    elif message.text == 'ГДЗ':
        back(message)
    elif message.text == 'Информация':
        title_about = f'Версия Бота: {version_bot} \nАвтор: @sobaka2227 \n Спонсоры: Vlad Khromin, Elizaveta Ryumina'

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Домой🏠']])
        bot.send_message(message.from_user.id, title_about, reply_markup=keyboard)


def subject(message):
    print(
        f'{time.ctime(time.time())} >> {message.text} : {message.from_user.first_name} : {message.from_user.last_name} : {message.from_user.username}')

    if message.text == 'Русский язык':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Упражнения']])
        keyboard.add(*[types.KeyboardButton(name) for name in ['Проверяем себя', 'Повторяем орфографию']])
        keyboard.add(*[types.KeyboardButton(name) for name in ['Назад']])
        send = bot.send_message(message.from_user.id, "Выберите то, что вам нужно", reply_markup=keyboard)
        bot.register_next_step_handler(send, rus_dop)

    elif message.text == 'Французский язык':
        send = bot.send_message(message.from_user.id, "Введите страницу")
        bot.register_next_step_handler(send, franc)

    elif message.text == 'Английский язык':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Учебник']])
        keyboard.add(*[types.KeyboardButton(name) for name in ['Activity Book']])
        keyboard.add(types.KeyboardButton("Reader"))
        keyboard.add(*[types.KeyboardButton(name) for name in ['Назад']])
        send = bot.send_message(message.from_user.id, "Выберите то, что вам нужно", reply_markup=keyboard)
        bot.register_next_step_handler(send, eng_dop)

    elif message.text == 'История':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('История России'))
        keyboard.add(types.KeyboardButton('Всеобщая История'))
        keyboard.add(types.KeyboardButton('Назад'))
        send = bot.send_message(message.from_user.id, "Выберите то, что вам нужно", reply_markup=keyboard)
        bot.register_next_step_handler(send, history_dop)

    elif message.text == 'Физика':
        send = bot.send_message(message.from_user.id, "Введите номер упражнения")
        bot.register_next_step_handler(send, fiz)

    elif message.text == 'Химия':
        send = bot.send_message(message.from_user.id, "Введите номер параграфа")
        bot.register_next_step_handler(send, chemistry)

    elif message.text == 'Математика':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Алгебра', 'Геометрия']])
        keyboard.add(*[types.KeyboardButton(name) for name in ['Д.М.Алгебра', 'Д.М.Геометрия']])
        keyboard.add(*[types.KeyboardButton(name) for name in ['Назад']])
        send = bot.send_message(message.from_user.id, "Выберите то, что вам нужно", reply_markup=keyboard)
        bot.register_next_step_handler(send, math_dop)

    elif message.text == 'Домой🏠':
        first(message)


def rus_dop(message):
    if message.text == 'Упражнения':
        send = bot.send_message(message.from_user.id, "Введите номер упражнения")
        bot.register_next_step_handler(send, rus_exercise)
    elif message.text == 'Повторяем орфографию':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(i[1], callback_data=f'rus_repeat_orpho_{i[0] + 1}')
                       for i in enumerate(['12', '100', '111', '127', '148', '253', '287', '337'])])
        send = bot.send_message(message.from_user.id, "Введите номер страницы", reply_markup=keyboard)
    elif message.text == 'Проверяем себя':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(i[1], callback_data=f'rus_check_yourself_{i[0] + 1}')
                       for i in enumerate(['12', '100', '111', '127', '148', '253', '287', '303', '337'])])
        send = bot.send_message(message.from_user.id, "Введите номер страницы", reply_markup=keyboard)
    elif message.text == 'Назад':
        back(message)


def franc(message):
    try:
        url = f"https://raw.githubusercontent.com/VladimirSource/imagesforbot/master/{message.text}_"
        parseBS(url, message, "Перевод и ответы на вопросы на странице", 3, 183, arr=[12])
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def history_dop(message):
    if message.text == 'История России':
        send = bot.send_message(message.from_user.id, "Введите номер параграфа")
        bot.register_next_step_handler(send, history_russian)
    elif message.text == 'Всеобщая История':
        send = bot.send_message(message.from_user.id, "Введите номер страницы")
        bot.register_next_step_handler(send, historyAll)
    elif message.text == 'Назад':
        back(message)


def engRead(message):
    try:
        url = f"https://raw.githubusercontent.com/VladimirSource/imagesforbot/master/9engRead{message.text}_"
        parseBS(url, message, "Решение и перевод заданий на странице", 5, 93, arr=[4])
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def historyAll(message):
    try:
        url = f"https://raw.githubusercontent.com/VladimirSource/imagesforbot/master/9hisAll{message.text}_"
        parseBS(url, message, "Ответы на вопросы на странице номер", 6, 225, arr=[12])
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def geom_didactic_materials(message, var):
    try:
        url = f"https://gdz.ru/class-9/geometria/didakticheskie-materiali-merzlyak/{var}-var-{message.text}/"
        parseBS(url, message, "Решение номера", 1, 307)
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def history_russian(message):
    try:
        paragraph = global_vars.main['historyRussian'].get(int(message.text), 0)
        if paragraph:
            url = f"https://gdz.ru/class-9/istoriya/arsentjev/{paragraph}-item/"
            parseBS(url, message, "Ответы на вопросы параграфа номер", 1, 42)
        else:
            bot.send_message(message.from_user.id, "Извините, на вопросы данного параграфа ответов нет.")
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def alg_didactic_materials(message, var):
    try:
        url = f"https://gdz.ru/class-9/algebra/didakticheskie-materiali-merzlyak/{var}-var-{message.text}/"
        parseBS(url, message, "Решение номера", 1, 245)
    except Exception as ex:
        print(ex)
    finally:
        back(message)


def chemistry(message):
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            *[types.InlineKeyboardButton(i + 1, callback_data=f'chemistry&paragraph={message.text}&number={i + 1}')
              for i in range(global_vars.main['chemistry'][int(message.text)])])
        bot.send_message(message.from_user.id, "Выберите номер", reply_markup=keyboard)
    except Exception as e:
        print(e)


def math_dop(message):
    if message.text == 'Алгебра':
        send = bot.send_message(message.from_user.id, "Введите номер упражнения")
        bot.register_next_step_handler(send, alg)

    elif message.text == 'Геометрия':
        send = bot.send_message(message.from_user.id, "Введите номер упражнения")
        bot.register_next_step_handler(send, geom)

    elif message.text == 'Д.М.Геометрия':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*[types.InlineKeyboardButton(i[1], callback_data=f'geom_didactic_materials_var_{i[0] + 1}')
                       for i in enumerate(['1', '2', '3'])])
        send = bot.send_message(message.from_user.id, "Выберите номер варианта", reply_markup=keyboard)

    elif message.text == 'Д.М.Алгебра':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*[types.InlineKeyboardButton(i[1], callback_data=f'alg_didactic_materials_var_{i[0] + 1}')
                       for i in enumerate(['1', '2', '3'])])
        send = bot.send_message(message.from_user.id, "Выберите номер варианта", reply_markup=keyboard)

    elif message.text == 'Назад':
        back(message)


def fiz(message):
    try:
        url = f'https://gdz.ru/class-11/fizika/rymkevich/{message.text}-nom/'
        parseBS(url, message, 'Решение упражнения', 1, 1244)
    except:
        bot.send_message(message.from_user.id, "Введите корректное значение номера")
    back(message)


def rus_exercise(message):
    try:
        url = f'https://gdz.ru/class-9/russkii_yazik/bystrova/{message.text}-nom/'
        parseBS(url, message, 'Решение упражнения', 1, 315)
    except:
        bot.send_message(message.from_user.id, "Введите корректное значение номера")
    back(message)


def eng_dop(message):
    if message.text == 'Учебник':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(i, callback_data=f'eng_textbook&unit={i}') for i in range(1, 8)])
        send = bot.send_message(message.from_user.id, "Выберите Unit", reply_markup=keyboard)
    elif message.text == "Reader":
        send = bot.send_message(message.from_user.id, "Введите номер страницы")
        bot.register_next_step_handler(send, engRead)
    elif message.text == 'Activity Book':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        send = bot.send_message(message.from_user.id, "Введите номер страницы", reply_markup=keyboard)
        bot.register_next_step_handler(send, eng_abb)
    elif message.text == 'Назад':
        back(message)


def eng_abb(message):
    try:
        url = f"https://gdz.ru/class-9/english/activity-book-kuzovlev/{message.text}-s/"
        parseBS(url, message, "Перевод и решение номеров на странице", 3, 142)
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Введите корректное значение номера")
    finally:
        back(message)


def alg(message):
    try:
        url = f'https://gdz.ru/class-9/algebra/merzlyak/{message.text}-nom/'
        parseBS(url, message, "Решение упражнения номер", 1, 1044)
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Введите корректное значение номера")
    back(message)


def geom(message):
    try:
        url = f'https://gdz.ru/class-9/geometria/merzlyak-polonskij/{message.text}-nom/'
        parseBS(url, message, 'Решение упражнения номер', 1, 887)
    except Exception as ex:
        print(ex)
        bot.send_message(message.from_user.id, "Введите корректное значение номера")
    back(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    if call.data.startswith('rus_repeat_orpho_'):
        try:
            url = f"https://gdz.ru/class-9/russkii_yazik/bystrova/1-pvtr-{call.data.lstrip('rus_repeat_orpho_')}/"
            parseBS(url, call, "Перевод и решение номеров на странице", 1, 9, permission=True)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Принято")
            back(call)
        except Exception as ex:
            print(ex)

    elif call.data.startswith('rus_check_yourself_'):
        try:
            url = f"https://gdz.ru/class-9/russkii_yazik/bystrova/2-pvtr-{call.data.lstrip('rus_check_yourself_')}/"
            parseBS(url, call, "Перевод и решение номеров на странице", 1, 10, permission=True)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Принято")
            back(call)
        except Exception as ex:
            print(ex)

    elif call.data.startswith('geom_didactic_materials_var_'):
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     text="Введите номер")
        bot.register_next_step_handler(send, geom_didactic_materials, call.data.lstrip('geom_didactic_materials_var_'))

    elif call.data.startswith('alg_didactic_materials_var_'):
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     text="Введите номер")
        bot.register_next_step_handler(send, alg_didactic_materials, call.data.lstrip('alg_didactic_materials_var_'))

    elif call.data.startswith('eng_textbook'):
        data = call.data.split('&')
        if "back" in call.data:
            data = data[:-2]
        if len(data) > 1:
            key = int(data[1].split('=')[1])
            if len(data) == 2:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    *[types.InlineKeyboardButton(i + 1, callback_data=f"eng_textbook&unit={key}&lesson={i + 1}")
                      for i in range(len(global_vars.main['eng_textbook'][key]))])
                keyboard.row(types.InlineKeyboardButton('back', callback_data=f'eng_textbook&unit={key}&lesson=back'))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Выберите урок", reply_markup=keyboard)
            elif len(data) == 3:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(*[types.InlineKeyboardButton(i + 1, callback_data=f"{call.data}&number={i + 1}") \
                               for i in range(global_vars.main['eng_textbook'][key][int(data[2].split('=')[1])])])
                keyboard.row(types.InlineKeyboardButton('back', callback_data=f'{call.data}&number=back'))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Выберите упражнение", reply_markup=keyboard)

            elif len(data) == 4:
                number = data[3].split('=')[1]
                url = f"https://gdz.ru/class-9/english/kuzovlev-12/{key}-{data[2].split('=')[1]}-u-{number}/"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Решение упражнения номер {number}")
                parseBS(url, call, 'Решение упражнения', 1, 15, permission=True)
                back(call)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(*[types.InlineKeyboardButton(i, callback_data=f'eng_textbook&unit={i}') for i in range(1, 8)])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите Unit", reply_markup=keyboard)
    elif call.data.startswith('chemistry'):
        data = call.data.split('&')
        paragraph = int(data[1].lstrip('paragraph='))
        number = int(data[2].lstrip('number='))
        url = f'https://gdz.ru/class-9/himiya/gabrielyan-9/{paragraph}-item-{number}/'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Решение номера {number}")
        parseBS(url, call, '', 1, 11, permission=True, condition='Решебник 1')
        back(call)

    elif call.data == 'answer_on_hw':
        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton('Отмена'))
        send = bot.send_message(call.from_user.id, 'Напишите ответным сообщение домашнее задание', reply_markup=kb)
        bot.register_next_step_handler(send, input_home_word)


if __name__ == '__main__':
    bot.polling(none_stop=True)
    while True:
        dateSTR = datetime.datetime.now().strftime("%H:%M:%S")
        if dateSTR == ("04:00:00"):
            try:
                DB.upload_file()
                time.sleep(1)
            except:
                pass
