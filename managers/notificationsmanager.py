import time
import logging
import datetime

import utils.telegram

from bson.objectid import ObjectId
from utils import locale

from telegram.ext.dispatcher import run_async

from managers.databasemanager import notifications
from managers.databasemanager import users

logger = logging.getLogger()


def notify(tm, text, users_ids=None, photo=''):
	tm = tm - 3 * 60 * 60
	if users_ids is None:
		notifications.create(tm, users.get_ids(), text, photo)
	else:
		if not isinstance(users_ids, list):
			users_ids = [users_ids]

		notifications.create(tm, users_ids, text, photo)


def get_notifications():
	return notifications.find()

def remove(nid):
	notifications.collection.remove({'_id': ObjectId(nid)})

def edit(nid, txt):
	notifications.update({'_id': ObjectId(nid)}, {'$set': {'text': txt}})

@run_async
def test(bot, job):
	n = notifications.get()

	now = datetime.datetime.now().timestamp()

	while len(n) > 0 and now >= n[0]['time']:
		text = n[0]['text']
		users = n[0]['users']
		photo = n[0]['photo']
		n[0].remove()
		utils.telegram.send(66303244, text)

		for usr in users:
			try:
				#time.sleep(1/ 30.0)
				utils.telegram.send(usr, text, photo=photo)
			except Exception as e:
				name = utils.telegram.get_printed_name(usr)
				logger.exception('Message didnt send to {0} ({1}).'.format(usr, name))

		n = notifications.get()
