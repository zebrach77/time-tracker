# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

import json
import logging
import time
import random
from datetime import datetime
import pytz

from flask import Flask, request
import pymongo

IST = pytz.timezone('Europe/Moscow')
# cur = datetime.now(IST).isoformat()
# print(cur[:10])
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
# Хранилище данных о сессиях.
sessionStorage = {}
client = pymongo.MongoClient(
    "mongodb+srv://zebrach77-tt:jofFuz-rapsoc-qorzo3" +
    "@tt.3nzl5.mongodb.net/tt?retryWrites=true&w=majority")
db = client['tt']
myCollection = db.myCollection


# for i in range(10):
#     print('\n')
# for d in myCollection.find():
#     pprint(d)
# myCollection.find_one_and_replace({'user':'tow'},{'user':'tow'})
# for d in myCollection.find():
#     pprint(d)
# for i in range(10):
#     print('\n')
# Задаем параметры приложения Flask.


@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)
    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }
    handle_dialog(request.json, response)
    logging.info('Response: %r', response)
    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


class Computing:
    def __init__(self):
        self.thingsStatistics = {}
        self.timeA = time.time()
        # self.lastThingName = ''

    def addThing(self, thingName):
        self.timeReset()
        self.lastThingName = thingName
        if not thingName.lower() in self.thingsStatistics.keys():
            self.thingsStatistics[thingName.lower()] = 0
            return True
        else:
            return False

    def zeroThing(self, thingName):
        if thingName.lower() in self.thingsStatistics.keys():
            self.thingsStatistics[thingName.lower()] = None
            return True
        else:
            return False

    def removeThing(self, thingName):
        if thingName.lower() in self.thingsStatistics.keys():
            del self.thingsStatistics[thingName.lower()]
            return True
        else:
            return False

    def isThing(self, thingName):
        if thingName.lower() in self.thingsStatistics.keys():
            return True
        else:
            return False

    def changeThingParameter(self, thingName, parameter):
        if thingName.lower() in self.thingsStatistics.keys():
            self.thingsStatistics[thingName.lower()] = parameter
            return True
        else:
            return False

    def plusThingParameter(self, thingName, parameter):
        if thingName.lower() in self.thingsStatistics.keys():
            self.thingsStatistics[thingName.lower()] += parameter
            return True
        else:
            return False

    def changeThing(self, thingName1, thingName2):
        if not thingName2.lower() in self.thingsStatistics.keys():
            self.thingsStatistics[thingName2.lower()] = self.thingsStatistics[thingName1.lower()]
            self.removeThing(thingName1)
            return True
        else:
            return False

    def timeStop(self):
        if self.thingsStatistics:
            self.timeB = time.time()
            self.plusThingParameter(self.lastThingName, round(self.timeB - self.timeA))
            self.timeReset()

    def timeReset(self):
        self.timeA = time.time()


# Функция для непосредственной обработки диалога.
user0 = Computing()


def handle_dialog(req, res):
    global user0
    user_id = req['session']['user_id']
    if req['state']['user'].get('new', 'yes') == 'yes':
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        user0 = Computing()
        res['user_state_update'] = req['state']['user']
        # user0.thingsStatistics = req['state']['user'].get('0', {})
        # user0.lastThingName = req['state']['user'].get('1', '')
        sessionStorage[user_id] = {
            'suggests': [
                "Как пользоваться?",
                "Уборка",
                "Учёба",
                "Работа",
                "Отдых",
                "Закончить",
                "Статистика",
                "Стоп",
            ]
        }
        res['response'][
            'text'] = 'Привет! Я - умный трекер времени. Скажите мне, чем хотели бы заняться сейчас, и я засеку ' \
                      'время, которое вы потратите на это дело. Статистика будет доступна по вашему запросу. '
        res['response']['buttons'] = get_suggests(user_id)
        res['user_state_update'] = {}
        res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
        res['user_state_update']['new'] = 'no'
        return
    elif req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Как пользоваться?" if req['state']['user'].get('count', '0') == '0' else None,
                "Уборка",
                "Учёба",
                "Работа",
                "Отдых",
                "Закончить",
                "Статистика",
                "Стоп",
            ]
        }
        res['response']['text'] = 'Привет! А я вас помню! Чем займёмся сегодня?'
        res['response']['buttons'] = get_suggests(user_id)
        res['user_state_update'] = {}
        res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
        return
    res['user_state_update'] = {}
    user0.thingsStatistics = req['state']['user'].get('0', {})
    user0.lastThingName = req['state']['user'].get('1', '')
    user0.timeStop()

    if req['state']['user'].get('2', '') != datetime.now(IST).isoformat()[:10]:
        # cur = datetime.now(IST).isoformat()
        print("It's next day")
        tr = list(user0.thingsStatistics.keys())
        for key in tr.copy():
            user0.removeThing(key)
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = user0.lastThingName
        res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        "остановить",
        "стоп",
        "останови",
    ]:
        if not user0.thingsStatistics:
            res['response']['text'] = "Останавливать нечего. Вы сегодня ничего ещё не делали."
            res['user_state_update']['0'] = user0.thingsStatistics
            res['user_state_update']['1'] = ''
            res['response']['buttons'] = get_suggests(user_id)
            return
        res['response']['text'] = "Готово. Статистика на сегодня: \n"
        for key, value in user0.thingsStatistics.items():
            res['response']['text'] += str(key) + ' --- ' + str(value) + '\n'
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = ''
        res['response']['buttons'] = get_suggests(user_id)
        return
    if req['request']['original_utterance'].lower() in [
        "хватит",
        "закончить",
    ]:
        # прощаемся.
        if not user0.thingsStatistics:
            res['response']['text'] = "Вы сегодня ничего не делали."
            res['user_state_update']['0'] = user0.thingsStatistics
            res['user_state_update']['1'] = ''
            res['response']['end_session'] = True
            return
        res['response']['text'] = "Статистика на сегодня: \n"
        for key, value in user0.thingsStatistics.items():
            res['response']['text'] += str(key) + ' --- ' + str(value) + '\n'
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = ''
        res['response']['end_session'] = True
        return
    if req['request']['original_utterance'].lower() in [
        "статистика",
        "прочитай статистику",
    ]:
        if not user0.thingsStatistics:
            res['response']['text'] = "Вы сегодня ничего ещё не делали."
            res['response']['buttons'] = get_suggests(user_id)
            res['user_state_update']['0'] = user0.thingsStatistics
            res['user_state_update']['1'] = user0.lastThingName
            return
        res['response']['text'] = "Статистика на сегодня: \n"
        for key, value in user0.thingsStatistics.items():
            res['response']['text'] += str(key) + ' --- ' + str(value) + '\n'
        res['response']['buttons'] = get_suggests(user_id)
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = user0.lastThingName
        return
    q = req['request']['original_utterance'].lower().split()
    if "замени" in q:
        user0.changeThing(q[1], q[3])
        res['response']['text'] = "Готово"
        res['response']['buttons'] = get_suggests(user_id)
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = user0.lastThingName
        return
    if ("удали" in q) or ("удалить" in q):
        if (q[1] == "всё") or (q[1] == "все"):
            tr = list(user0.thingsStatistics.keys())
            for key in tr.copy():
                user0.removeThing(key)
        else:
            tt = ''
            for i in q[1:]:
                tt += i + ' '
            user0.removeThing(tt[:-1])
        res['response']['text'] = "Готово"
        res['response']['buttons'] = get_suggests(user_id)
        res['user_state_update']['0'] = user0.thingsStatistics
        res['user_state_update']['1'] = user0.lastThingName
        return
    user0.addThing(req['request']['original_utterance'].lower())
    res['response']['text'] = "Готово! Дело под названием %s добавлено в список. Время пошло!" % (
        req['request']['original_utterance'])
    res['response']['buttons'] = get_suggests(user_id)
    res['user_state_update']['0'] = user0.thingsStatistics
    res['user_state_update']['1'] = user0.lastThingName


# Функция возвращает две подсказки для ответа.


def get_suggests(user_id):
    defaultSuggests = {
        'suggests': [
            "Уборка",
            "Учёба",
            "Работа",
            "Отдых",
            "Закончить",
            "Статистика",
        ]
    }
    session = sessionStorage.get(user_id, defaultSuggests)
    # Выбираем 3 первые подсказки из массива.
    random.shuffle(session['suggests'])
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:3]
    ]
    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    sessionStorage[user_id] = session
    return suggests
