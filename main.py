import os
import json
import time
from threading import Thread
# from multiprocessing import Process
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

skeit_park = "http://95.215.176.83:10090/video5.mjpg?resolution=730x410&amp;fps="
tennis_cort = "http://95.215.176.83:10090/video33.mjpg?resolution=&fps="
central_entry = "http://95.215.176.83:10090/video14.mjpg?resolution=&fps="
alley = "http://95.215.176.83:10090/video7.mjpg?resolution=&fps="
circle = "http://95.215.176.83:10090/video19.mjpg?resolution=&fps="
#attractions = "http://95.215.176.83:10090/video34.mjpg?resolution=&fps="

locations = [skeit_park, tennis_cort, central_entry, alley, circle]
locations_name = ["skeit_park", "tennis_cort", "central_entry", "alley", "circle"]
locations_bd = {}

def data_parse():
    data = str(datetime.now())
    arr = data.split(' ')
    day = int(arr[0].split('-')[2])
    arr2 = arr[1].split(':')
    hour = int(arr2[0])
    minute = int(arr2[1])
    return day, hour, minute

def db_entry(name_location, count):
    day, hour, minute = data_parse()
    if not name_location in locations_bd:
        list_day = dict()
        locations_bd[name_location] = list_day
    if not day in locations_bd[name_location]:
        list_hour = dict()
        locations_bd[name_location][day] = list_hour
    if not hour in locations_bd[name_location][day]:
        list_minute = dict()
        locations_bd[name_location][day][hour] = list_minute
    locations_bd[name_location][day][hour][minute] = count

def average_search_day(day1, day2, locations_bd, name_location):
    listi = []
    finish = 0
    average = 0
    count = 0
    while day1 <= day2:
        hour = 0
        tmp_average = 0
        tmp_count = 0
        if locations_bd[name_location]:
            while hour <= 23:  
                if hour in locations_bd[name_location][day1]:
                    minute = 0
                    while minute <= 60:
                        if minute in locations_bd[name_location][day1][hour]:
                            average += int(locations_bd[name_location][day1][hour][minute])
                            tmp_average += int(locations_bd[name_location][day1][hour][minute])
                            tmp_count += 1
                            count += 1
                        minute += 1
                hour += 1
        day1 += 1
        if tmp_count != 0:
            listi.append(int(tmp_average / tmp_count))
    if (count != 0):
        finish += average / count
    return finish, listi

def average_search_hour(hour1, hour2, locations_bd, name_location, day):
    listi = []
    finish = 0
    count = 0
    average = 0
    if locations_bd:
        if day in locations_bd[name_location]:
            while hour1 <= hour2:
                if hour1 in locations_bd[name_location][day]:
                    minute = 0
                    tmp_count = 0
                    tmp_average = 0
                    while minute <= 60:
                        if minute in locations_bd[name_location][day][hour1]:
                            average += int(locations_bd[name_location][day][hour1][minute])
                            tmp_average += int(locations_bd[name_location][day][hour1][minute])
                            count += 1
                            tmp_count += 1
                        minute += 1
                    if tmp_count != 0:
                        listi.append(int(tmp_average / tmp_count))
                hour1 += 1
    if count != 0:
        finish += average / count
    return finish, listi

def average_search_minute(minute1, minute2, locations_bd, name_location, day, hour):
    listi = []
    listi2 = []
    finish = 0
    count = 0
    average = 0
    if name_location in locations_bd:
        if day in locations_bd[name_location]:
            if hour in locations_bd[name_location][day]:
                while minute1 <= minute2:
                    if minute1 in locations_bd[name_location][day][hour]:
                        average += int(locations_bd[name_location][day][hour][minute1])
                        listi.append(int(locations_bd[name_location][day][hour][minute1]))
                        listi2.append(int(minute1))
                        count += 1
                    elif not minute1 % 5:
                        listi.append(0)
                        listi2.append(minute1)
                    minute1+= 1
                finish += average / count
    return finish, listi, listi2

def count_statistics(start, end, name_location, hour, day):
    z = []
    if hour != -1:
        i, l, l2 = average_search_minute(start, end, locations_bd, name_location, day, hour)
        j = 0
        while (j < len(l2)):
            z.append(l2[j])
            j += 1
        j += 1
    elif day != -1:
        i, l = average_search_hour(start, end, locations_bd, name_location, day)
        while start <= end:
            start += 1
    else:
        i, l = average_search_day(start, end, locations_bd, name_location)
        while start <= end:
            z.append(j)
            start += 1
    x = range(len(l))
    return i

def count_people(json_file):
    with open(json_file, "r") as f:
        i = f.read().count("person")
    return i

def get_photo(name, path):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)
        driver.set_page_load_timeout(2)
        driver.get(path)

    except Exception as e:
        driver.save_screenshot('photo/'+str(name)+'.png')
        driver.close()

def get_peoples():
    #os.system('flow --imgdir photo/ --model cfg/yolo.cfg --load bin/yolo.weights')
    os.system('flow --imgdir photo/ --model cfg/yolo.cfg --load bin/yolo.weights --json')

def crowd_stats():
    while True:
        j = 0
        for i in locations:
            get_photo(locations_name[j], i)
            j += 1
        get_peoples()
        for i in locations_name:
            count = count_people('photo/out/' + i + '.json')
            db_entry(i, count)
        time.sleep(60 * 5)

def now_stats(m):
    k = 0
    day, hour, minute = data_parse()
    string = ""
    s = ""
    for i in locations_name:
        if m == 0:
            s2 = "за 5 минут"
            j = count_statistics(minute -5, minute + 5, i, hour, day)
        elif m == 1:
            s2 = "за 15 минут"
            if minute < 15:
                j = count_statistics(0, 15, i, hour - 1, day)
            else:
                j = count_statistics(minute - 16, minute, i, hour, day)
        elif m == 2:
            s2 = "за 30 минут"
            if minute < 30:
                j = count_statistics(0, 30, i, hour - 1, day)
            else:
                j = count_statistics(minute - 31, minute, i, hour, day)
        elif m == 3:
            s2 = "за час"
            j = count_statistics(0, 60, i, hour - 1, day)
        elif m == 4:
            s2 = "за день"
            j = count_statistics(0, 12, i, -1, day)
        if k == 0:
            s = "<Скейт-зал>"
            t1 = "Средний поток посетителей на локации {} {}: {}\n\n".format(s, s2, int(j))
        elif k == 1:
            s = "<Зал для пин-понга>"
            t2 = "Средний поток посетителей на локации {} {}: {}\n\n".format(s, s2, int(j))
        elif k == 2:
            s = "<Главный вход>"
            t3 = "Средний поток посетителей на локации {} {}: {}\n\n".format(s, s2, int(j))
        elif k == 3:
            s = "<Центральная аллея>"
            t4 = "Средний поток посетителей на локации {} {}: {}\n\n".format(s, s2, int(j))
        elif k == 4:
            s = "<Большой круг>"
            t5 = "Средний поток посетителей на локации {} {}: {}\n\n".format(s, s2, int(j))
        k += 1
    if k == 5:
        return t1 + t2 + t3 + t4 + t5

def stats_bot():
    updater = Updater(token='810960806:AAHMOaKrwMYOPbolF92Nrv6DQYwYYXEbI_E')
    dp = updater.dispatcher

    def start(bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                text="Привет! Я аналитический бот Crowd Statistics, созданный в рамках хакатона VisionLabs в Школе 21.\n"
                "\nЯ с помощью нейросети в реальном времени собираю статистику о количестве людей с публичных камер в парке Сокольники.\n"
                "В данный момент статистика собирается с 5 камер."
                "\nЛокации: главный вход в парк, центральная аллея, большой круг, скейт-зал, зал для пинпонга.")
        bot.send_message(chat_id=update.message.chat_id, 
            text="Какую статистику вы бы хотели узнать?\n\n"
            "[1] За последние 5 минут\n"
            "[2] За последние 15 минут\n"
            "[3] За последние 30 минут\n"
            "[4] За последний час\n"
            "[5] За день\n")
    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    def echo(bot, update):
        if update.message.text == '1':
            string = now_stats(0)
            bot.send_message(chat_id=update.message.chat_id, text=string)
        elif update.message.text == '2':
            string = now_stats(1)
            bot.send_message(chat_id=update.message.chat_id, text=string)
        elif update.message.text == '3':
            string = now_stats(2)
            bot.send_message(chat_id=update.message.chat_id, text=string)
        elif update.message.text == '4':
            string = now_stats(3)
            bot.send_message(chat_id=update.message.chat_id, text=string)
        elif update.message.text == '5':
            string = now_stats(4)
            bot.send_message(chat_id=update.message.chat_id, text=string)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Выберите вариант от [1] до [5]")
    echo_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(echo_handler)

    def unknown(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Я не понял команду.\nПовторите пожалуйста!")
    unknown_handler = MessageHandler(Filters.command, unknown)
    dp.add_handler(unknown_handler)

    updater.start_polling()


if __name__ == '__main__':
    p1 = Thread(target = crowd_stats)
    p2 = Thread(target = stats_bot)

    p1.start()
    p2.start()
    # Process(target=stats_bot).start()
    # Process(target=crowd_stats).start()
    # crowd_stats()
    # stats_bot()