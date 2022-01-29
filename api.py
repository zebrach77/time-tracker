# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

import json
import logging
import random
from datetime import datetime
import pytz

from flask import Flask, request

IST = pytz.timezone('Europe/Moscow')
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)




# Хранилище данных о сессиях.

# client = pymongo.MongoClient(
#     "mongodb+srv://zebrach77-tt:jofFuz-rapsoc-qorzo3" +
#     "@tt.3nzl5.mongodb.net/tt?retryWrites=true&w=majority")
# db = client['tt']
# myCollection = db.myCollection


def popf(l, el):
    if el in l:
        l.remove(el)
    return l


class Computing:
    def __init__(self):
        self.thingsStatistics = {}
        self.projects = {}
        self.timeA = datetime.now()
        self.timeB = datetime.now()
        self.lastThingName = ''
        self.lastProjectName = 'Default'

    def getProjStats(self, projName='Default'):
        self.projects[self.lastProjectName] = self.thingsStatistics
        self.lastProjectName = projName
        self.thingsStatistics = self.projects.get(projName, {})

    def addThing(self, thingName):
        # self.timeReset()
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
            self.timeB = datetime.now()
            logging.warning([self.timeB - self.timeA])
            self.plusThingParameter(self.lastThingName, (self.timeB - self.timeA).seconds)
        self.timeReset()

    def timeReset(self):
        self.timeA = datetime.now()


class Processing:
    def __init__(self, reqT, resT, comp):
        self.res = resT
        self.req = reqT
        self.sessionStorage = {}
        self.res['user_state_update'] = {}
        self.user = comp
        # if self.req:
        self.user_id = self.req['session']['user_id']
        self.user.thingsStatistics = self.req['state']['user'].get('0', {})
        self.user.lastThingName = self.req['state']['user'].get('1', '')
        self.mode = self.req['state']['user'].get('mode', 0)
        self.projMode = self.req['state']['user'].get('proj_mode', 0)
        self.ans = self.req['request']['original_utterance'].lower().split()
        self.audioDefaults = {
            'tudu': "<speaker audio=\"dialogs-upload/46d0e1e5-cba1-4eb7-914a-2045510d3a3b/95cbe457-cc88-4389-901d-89b25edd36ab.opus\">"}
        self.mainControl()

    def h(self, dig):
        if dig == 1:
            return "час"
        if (dig == 0) or (dig >= 5):
            return "часов"
        if (dig == 2) or (dig == 3) or (dig == 4):
            return "часа"

    def m(self, dig):
        if dig == 1:
            return "минута"
        if (dig == 0) or (dig >= 5):
            return "минут"
        if (dig == 2) or (dig == 3) or (dig == 4):
            return "минуты"

    def s(self, dig):
        if dig == 1:
            return "секунда"
        if (dig == 0) or (dig >= 5):
            return "секунд"
        if (dig == 2) or (dig == 3) or (dig == 4):
            return "секунды"

    def secondsToTime(self, val):
        tm = ''
        secs = val % 60
        mins = val // 60
        hours = val // 3600
        if hours:
            tm += "%d %s, " % (hours, self.h(hours % 10)) if (hours <= 10) or (hours >= 20) else "%d %s, " % (
                hours, self.h(0))
        if mins:
            tm += "%d %s, " % (mins, self.m(mins % 10)) if (mins <= 10) or (mins >= 20) else "%d %s, " % (
                mins, self.m(0))
        if secs:
            tm += "%d %s" % (secs, self.s(secs % 10)) if (secs <= 10) or (secs >= 20) else "%d %s, " % (secs, self.s(0))
        return tm

    def contUser(self):
        self.sessionStorage[self.user_id] = {
            'suggests': [
                "Как пользоваться?" if self.req['state']['user'].get('count', '0') == '0' else None,
                "Настройка",
                "Уборка",
                "Учёба",
                "Работа",
                "Отдых",
                "Закончить",
                "Статистика",
                "Стоп",
            ]
        }
        self.res['response']['text'] = 'Привет! А я вас помню! Чем займёмся сегодня?'
        self.dup1()
        return

    def newUser(self):
        self.sessionStorage[self.user_id] = {
            'suggests': [
                "Как пользоваться?",
                "Настройка",
                "Уборка",
                "Учёба",
                "Работа",
                "Отдых",
                "Закончить",
                "Статистика",
                "Стоп",
            ]
        }
        self.res['response'][
            'text'] = 'Привет! Я - умный трекер времени. Скажите мне, чем хотели бы заняться сейчас, и я засеку ' \
                      'время, которое вы потратите на это дело. Статистика будет доступна по вашему запросу. ' \
                      'Для настройки скажите кодовое слово Настройка. Для инструкции по использованию навыка скажите ' \
                      'Как пользоваться?'


        self.dup1()

    def stopR(self, b):
        if not self.user.thingsStatistics:
            self.res['response'][
                'text'] = "Останавливать нечего. Вы сегодня ничего ещё не делали." if b else "Вы сегодня ничего не делали."
        else:
            self.res['response']['text'] = "Готово. "
        self.stats()
        self.res['user_state_update']['0'] = self.user.thingsStatistics
        self.res['user_state_update']['1'] = ''
        self.res['response']['buttons'] = self.get_suggests(self.user_id)
        return

    def get_suggests(self, user_id):
        defaultSuggests = {
            'suggests': [
                "Настройка",
                "Уборка",
                "Учёба",
                "Работа",
                "Отдых",
                "Закончить",
                "Статистика",
            ]
        }
        session = self.sessionStorage.get(user_id, defaultSuggests)
        random.shuffle(session['suggests'])
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in (
                ["Как пользоваться?"] + popf(session['suggests'][:3], "Как пользоваться?") if "Как пользоваться?" in
                                                                                              session['suggests'] else
                session['suggests'][:3])
        ]
        self.sessionStorage[user_id] = session
        return suggests

    def nextDay(self):
        print("It's next day")
        tr = list(self.user.thingsStatistics.keys())
        for key in tr.copy():
            self.user.removeThing(key)
        self.res['user_state_update']['0'] = {}
        self.res['user_state_update']['1'] = ''
        self.res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]

    def stats(self):

        if not self.user.thingsStatistics:
            self.res['user_state_update']['0'] = {}
            self.res['user_state_update']['1'] = ''
            return
        self.res['response']['text'] = self.res['response'].get('text', '') + "Статистика на сегодня: \n"
        for key, value in self.user.thingsStatistics.items():
            self.res['response']['text'] += str(key) + ' --- ' + self.secondsToTime(value) + '\n'
        self.dup1()

    def dup1(self, audio=''):
        self.res['response']['buttons'] = self.get_suggests(self.user_id)
        self.res['user_state_update']['0'] = self.user.thingsStatistics
        self.res['user_state_update']['1'] = self.user.lastThingName
        self.res['user_state_update']['new'] = 'no'
        self.res['response']['tts'] = audio + self.res['response']['text']
        # self.res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
        return

    def dup2(self):
        self.sessionStorage[self.user_id] = {
            'suggests': [
                "Включить режим проектов",
                "Выключить режим проектов",
                "Режим проектов",
                "Как пользоваться?",
                "Остановить настройку"
            ]
        }
        self.res['response']['buttons'] = self.get_suggests(self.user_id)
        self.res['user_state_update']['0'] = self.user.thingsStatistics
        self.res['user_state_update']['1'] = self.user.lastThingName
        self.res['user_state_update']['new'] = 'no'
        # self.res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
        return

    def variants(self):
        if "замени" in self.ans:
            self.user.changeThing(self.ans[1], self.ans[3])
            self.res['response']['text'] = "Готово"
            self.dup1(self.audioDefaults['tudu'])
            return
        if ("удали" in self.ans) or ("удалить" in self.ans):
            if (self.ans[1] == "всё") or (self.ans[1] == "все"):
                tr = list(self.user.thingsStatistics.keys())
                for key in tr.copy():
                    self.user.removeThing(key)
                tempBool = True
            else:
                tempBool = False
                tt = ''
                for i in self.ans[1:]:
                    tt += i + ' '
                tempBool = self.user.removeThing(tt[:-1])
            if tempBool:
                self.res['response']['text'] = "Готово"
                self.dup1(self.audioDefaults['tudu'])
            else:
                self.res['response']['text'] = "Не получилось найти это дело. Попробуйте ещё раз."
                self.dup1()
            return
        if self.req['request']['original_utterance'].lower() not in self.user.thingsStatistics:
            self.user.addThing(self.req['request']['original_utterance'].lower())
            self.res['response']['text'] = "Готово! Дело под названием %s добавлено в список. Время пошло!" % (
                self.req['request']['original_utterance'])
        else:
            self.user.addThing(self.req['request']['original_utterance'].lower())
            self.res['response']['text'] = "Хорошо! Продолжаю считать время дела под названием %s" % \
                                           self.req['request']['original_utterance']
        self.dup1(self.audioDefaults['tudu'])
        return

    def mainA(self):
        if self.req['state']['user'].get('new', 'yes') == 'yes':
            self.newUser()
            return
        elif self.req['session']['new']:
            self.contUser()
            return
        self.user.timeStop()
        if self.req['request']['original_utterance'].lower() in [
            "настройки",
            "настройка"
        ]:
            self.res['user_state_update']['mode'] = 1
            self.res['response']['text'] = 'Добро пожаловать в меню настройки! \n' \
                                           'Здесь пока ничего нет, если у вас есть идеи, что сюда добавить, ' \
                                           'напишите на почту разработчику:\n' \
                                           'tchanov.gleb@yandex.ru'
            self.dup1()
            return
        if self.req['state']['user'].get('2', '') != datetime.now(IST).isoformat()[:10]:
            self.nextDay()
        if self.req['request']['original_utterance'].lower() in [
            "остановить",
            "останови"
        ]:
            self.stopR(True)
            self.dup1()
            return
        if self.req['request']['original_utterance'].lower() in [
            "хватит",
            "стоп",
            "закончить"
        ]:
            self.stopR(False)
            self.res['response']['end_session'] = True
            return
        if self.req['request']['original_utterance'].lower() in [
            "как пользоваться",
            "как пользоваться?",
            "документация"
        ]:
            self.res['response']['text'] = "Документация: \n" \
                                           "Для добавления дела в список дел и начала отсчёта просто скажите его название. \n" \
                                           "Помните, что тайм-трекер не умеет обрабатывать падежи и формы названий ваших дел. Поэтому всегда " \
                                           "произносите названия " \
                                           "так, как вы хотели бы их услышать при перечислении. \n" \
                                           "Правильный пример: 'Работа', 'Прогулка', и т. д. Старайтесь использовать существительные в именительном " \
                                           "падеже. \n\n" \
                                           "Для изменения одного названия на другое скажите 'Замени (текущее название) " \
                                           "на (замена названию)'\n" \
                                           "Например: 'Замени прогулка на обед' \n" \
                                           "Для удаления названия из списка скажите 'Удали (название)' \n" \
                                           "Для остановки отсчёта времени скажите 'Остановить'. Произносить название дела не нужно. \n"
            self.dup1()
            return

        if self.req['request']['original_utterance'].lower() in [
            "статистика",
            "прочитай статистику",
        ]:
            if not self.user.thingsStatistics:
                self.res['response']['text'] = "Вы сегодня ничего не делали."
                self.dup1()
            else:
                self.stats()
            return
        self.variants()
        return

    def projWrap(self, func_without_proj, projName = ''):
        def wrapper(*args, **kwargs):
            if projName:
                self.user.getProjStats(projName)
            else:
                self.user.getProjStats(self.user.lastProjectName)
            res = func_without_proj(*args, **kwargs)
            return res

        return wrapper

    def mainAProj(self):
        answ = self.req['request']['original_utterance'].lower()
        if ("добавь проект" in answ) or ("новый проект" in answ) or ("смени проект" in answ) or (
                "другой проект" in answ):
            tt = ''
            for i in self.ans[2:]:
                tt += i + ' '
            self.projWrap(self.mainA, tt)
        elif "проект" in self.ans:
            tt = ''
            for i in self.ans[1:]:
                tt += i + ' '
            self.projWrap(self.mainA, tt)
        else:
            self.projWrap(self.mainA)
        # self.res["response"]["text"] = "Готово."
        self.dup2()
        return

    def mainConfig(self):
        if self.req['request']['original_utterance'].lower() in [
            "режим проектов",
            "переключи режим проектов",
            "переключить режим проектов"
        ]:
            self.res["user_state_update"]["proj_mode"] = not self.req['state']['user'].get("proj_mode", 0)
            self.res["response"]["text"] = "Готово."
            self.dup2()
            return
        if self.req['request']['original_utterance'].lower() in [
            "включи режим проектов",
            "включить режим проектов"
        ]:
            self.res["user_state_update"]["proj_mode"] = 1
            self.res["response"]["text"] = "Готово. Теперь вы сможете выбирать проекты для своих задач."
            self.dup2()
            return
        if self.req['request']['original_utterance'].lower() in [
            "выключи режим проектов",
            "выключить режим проектов",
            "отключи режим проектов",
            "отключить режим проектов"
        ]:
            self.res["user_state_update"]["proj_mode"] = 0
            self.res["response"]["text"] = "Готово. Режим проектов отключён."
            self.dup2()
            return
        if self.req['request']['original_utterance'].lower() in [
            "как пользоваться",
            "как пользоваться?"
        ]:
            self.res['response']['text'] = "Добро пожаловать в меню настройки!\n" \
                                           "В данный момент для настройки доступны следующие функции: \n" \
                                           "1. Переключение/включение/выключпение режима проектов. \n" \
                                           "    Режим проектов позволяет присвоить каждой задаче по одному проекту. " \
                                           "Можно выбрать, оплачиваемый ли проект. Можно выбрать один из 5 звуков " \
                                           "индивидуально для каждого проекта."
            self.dup2()
            return
        if self.req['request']['original_utterance'].lower() in [
            "остановить",
            "останови",
            "остановить настройку",
            "останови настройку"
        ]:
            self.res['user_state_update']['mode'] = 0
            self.res['response']['text'] = "Хорошо. Применяю настройки и перехожу в режим использования."
            return

    def mainControl(self):
        if self.mode == 0:
            if self.projMode == 0:
                self.mainA()
            else:
                self.mainAProj()
            return
        if self.mode == 1:
            self.mainConfig()
            return


comp = Computing()


@app.route("/", methods=['POST'])
def main():
    global comp
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)
    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }
    dialog0 = Processing(request.json, response, comp)
    response = dialog0.res
    comp = dialog0.user
    logging.info('Response: %r', response)
    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )
