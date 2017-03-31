import logging
from threading import Lock

from managers.databasemanager import users
from entities.user import User
from utils import telegram

from telegram.ext import Job

logger = logging.getLogger()
locks = {}


class UserContext():
	def __init__(self, uid):
		self.uid = uid

		if self.uid not in locks:
			locks[self.uid] = Lock()

	def __enter__(self):
		locks[self.uid].acquire()
		self.usr = get_user(self.uid)
		return self.usr

	def __exit__(self, type, value, traceback):
		if save_user(self.usr):
			self.usr.nickname, self.usr.name = telegram.get_names(self.usr.uid)
			save_user(self.usr)

		locks[self.uid].release()

		while len(telegram.jobs_to_add) > 0:
			uid, func, time, repeat, context = telegram.jobs_to_add.pop()

			j = Job(call_func, time, repeat=repeat, context=(uid, func, context))
			telegram.updater.job_queue.put(j)


def call_func(bot, job):
	uid, func, context = job.context

	with UserContext(uid) as usr:
		foo = getattr(usr, func)
		if foo is not None and foo(context):
			job.schedule_removal()


def get_user(uid):
	d = users.get_user(uid)
	u = User(uid)

	if d is not None:
		for k in d.keys():
			setattr(u, k, d[k])

	return u


def save_user(usr):
	return users.save_user(usr.__dict__)


def msg(uid, update):
	with UserContext(uid) as usr:
		usr.message(update)


def inline_button(uid, msg_id, content):
	with UserContext(uid) as usr:
		usr.inline_button(msg_id, content)


def start(uid, is_admin=False):
	with UserContext(uid) as usr:
		usr.is_admin = usr.is_admin or is_admin
		usr.start()


def promote(uid):
	with UserContext(uid) as usr:
		usr.is_admin = not usr.is_admin
		return usr.is_admin