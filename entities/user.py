import logging

from managers import usermanager

logger = logging.getLogger()

from utils import locale
from utils import telegram

from managers.databasemanager import variables


class User(object):
	def __init__(self, uid):
		super(User, self).__init__()

		self.uid = uid
		self.state = 'menu'
		self.additional_state = ''

		self.nickname = ''
		self.name = ''

		self.is_admin = False

	def message(self, update):
		txt = update.message.text

		# code goes here

	def start(self, msg=None, btns=None):
		self.state = 'menu'

		if msg is None:
			msg = locale.get('menu.start')
		if btns is None:
			btns = [ ]

			if self.is_admin:
				pass


		self.send(msg, buttons=btns)

	def inline_button(self, msg_id, content):
		method, *args = content


	def send(self, *args, **kvargs):
		return telegram.send(self.uid, *args, **kvargs)
