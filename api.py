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

client = pymongo.MongoClient(
	"mongodb+srv://zebrach77-tt:jofFuz-rapsoc-qorzo3" +
	"@tt.3nzl5.mongodb.net/tt?retryWrites=true&w=majority")
db = client['tt']
myCollection = db.myCollection


def popf(l, el):
	if el in l:
		l.remove(el)
	return l


class Computing:
	def __init__(self):
		self.thingsStatistics = {}
		self.timeA = time.time()
		self.timeB = time.time()
		self.lastThingName = ''

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


class Processing:
	def __init__(self, reqT, resT):
		self.res = resT
		self.req = reqT
		self.user = Computing()
		self.sessionStorage = {}
		self.res['user_state_update'] = {}
		if self.req:
			self.user_id = self.req['session']['user_id']
			self.user.thingsStatistics = self.req['state']['user'].get('0', {})
			self.user.lastThingName = self.req['state']['user'].get('1', '')
			self.ans = self.req['request']['original_utterance'].lower().split()
			self.mainF()

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

	def secsToTime(self, val):
		secs_all = val
		tm = ''
		secs = secs_all % 60
		mins = secs_all // 60
		hours = secs_all // 3600
		if hours:
			tm += "%d %s, " % (hours, self.h(hours % 10))
		if mins:
			tm += "%d %s, " % (mins, self.m(mins % 10))
		if secs:
			tm += "%d %s" % (secs, self.s(secs % 10))
		return tm

	def initUser(self):
		self.res['user_state_update'] = self.req['state']['user']
		self.res['response']['buttons'] = self.get_suggests(self.user_id)
		self.res['user_state_update'] = {}
		self.res['user_state_update']['1'] = ''
		self.res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]
		self.res['user_state_update']['new'] = 'no'
		return

	def contUser(self):
		self.sessionStorage[self.user_id] = {
			'suggests': [
				"Как пользоваться?" if self.req['state']['user'].get('count', '0') == '0' else None,
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
		self.initUser()
		return

	def newUser(self):
		self.sessionStorage[self.user_id] = {
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
		self.res['response'][
			'text'] = 'Привет! Я - умный трекер времени. Скажите мне, чем хотели бы заняться сейчас, и я засеку ' \
		              'время, которое вы потратите на это дело. Статистика будет доступна по вашему запросу. '
		self.initUser()

	def stopR(self, b):
		if not self.user.thingsStatistics:
			self.res['response'][
				'text'] = "Останавливать нечего. Вы сегодня ничего ещё не делали." if b else "Вы сегодня ничего не делали."
		else:
			self.res['response']['text'] = "Готово."
		self.stats()
		self.res['user_state_update']['0'] = self.user.thingsStatistics
		self.res['user_state_update']['1'] = ''
		self.res['response']['buttons'] = self.get_suggests(self.user_id)
		return

	def get_suggests(self, user_id):
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
		self.res['user_state_update']['0'] = self.user.thingsStatistics
		self.res['user_state_update']['1'] = ''
		self.res['user_state_update']['2'] = datetime.now(IST).isoformat()[:10]

	def stats(self):
		if not self.user.thingsStatistics:
			self.res['user_state_update']['0'] = {}
			self.res['user_state_update']['1'] = ''
			return
		self.res['response']['text'] = self.res['response'].get('text', '') + "Статистика на сегодня: \n"
		for key, value in self.user.thingsStatistics.items():
			self.res['response']['text'] += str(key) + ' --- ' + self.secsToTime(value) + '\n'

	def dup1(self):

		self.res['response']['buttons'] = self.get_suggests(self.user_id)
		self.res['user_state_update']['0'] = self.user.thingsStatistics
		self.res['user_state_update']['1'] = self.user.lastThingName
		return

	def variants(self):
		if "замени" in self.ans:
			self.user.changeThing(self.ans[1], self.ans[3])
			self.res['response']['text'] = "Готово"
			self.dup1()
			return
		if ("удали" in self.ans) or ("удалить" in self.ans):
			if (self.ans[1] == "всё") or (self.ans[1] == "все"):
				tr = list(self.user.thingsStatistics.keys())
				for key in tr.copy():
					self.user.removeThing(key)
			else:
				tt = ''
				for i in self.ans[1:]:
					tt += i + ' '
				self.user.removeThing(tt[:-1])
			self.res['response']['text'] = "Готово"
			self.dup1()
			return
		if self.req['request']['original_utterance'].lower() not in self.user.thingsStatistics:
			self.user.addThing(self.req['request']['original_utterance'].lower())
			self.res['response']['text'] = "Готово! Дело под названием %s добавлено в список. Время пошло!" % (
				self.req['request']['original_utterance'])
		else:
			self.user.addThing(self.req['request']['original_utterance'].lower())
			self.res['response']['text'] = "Хорошо! Продолжаю считать время дела под названием %s" % \
			                               self.req['request'][
				                               'original_utterance']
		self.dup1()
		return

	def mainF(self):
		if self.req['state']['user'].get('new', 'yes') == 'yes':
			self.newUser()
			return
		if self.req['session']['new']:
			self.contUser()
			return
		self.user.timeStop()
		if self.req['state']['user'].get('2', '') != datetime.now(IST).isoformat()[:10]:
			self.nextDay()
		if self.req['request']['original_utterance'].lower() in [
			"остановить",
			"стоп",
			"останови",
		]:
			self.stopR(True)
			return
		if self.req['request']['original_utterance'].lower() in [
			"хватит",
			"закончить",
		]:
			self.stopR(False)
			self.res['response']['end_session'] = True
			return
		if self.req['request']['original_utterance'].lower() in [
			"статистика",
			"прочитай статистику",
		]:
			if not self.user.thingsStatistics:
				self.res['response']['text'] = "Вы сегодня ничего не делали."
			self.stats()
			return
		self.variants()
		return


dialog0 = Processing({}, {})


@app.route("/", methods=['POST'])
def main():
	global dialog0
	# Функция получает тело запроса и возвращает ответ.
	logging.info('Request: %r', request.json)
	response = {
		"version": request.json['version'],
		"session": request.json['session'],
		"response": {
			"end_session": False
		}
	}
	try:
		dialog0.mainF()
	except NameError:
		dialog0 = Processing(request.json, response)
	response = dialog0.res
	logging.info('Response: %r', response)
	return json.dumps(
		response,
		ensure_ascii=False,
		indent=2
	)
