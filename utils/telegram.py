import json
import telegram

from collections import deque

from managers.databasemanager import users

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

updater = None
last_update = None
jobs_to_add = deque()


def send(uid, text, buttons=None, picute=None, parse_mode=None, photo='', edit_id=None):
	bot = updater.bot

	if parse_mode == 'markdown':
		parse_mode = telegram.ParseMode.MARKDOWN

	def sendMessage(**kvargs):
		if edit_id is not None:
			return bot.editMessageText(chat_id=uid,
									   message_id=edit_id,
									   parse_mode=parse_mode,
									   text=text,
									   **kvargs)
		elif photo != '':
			return bot.sendPhoto(uid, photo=photo, caption=text, **kvargs)
		else:
			return bot.sendMessage(uid, parse_mode=parse_mode, text=text, **kvargs)

	if buttons:
		custom_keyboard = []

		for b in buttons:
			if isinstance(b, list):
				custom_keyboard.append(b)
			else:
				custom_keyboard.append([b])

		if isinstance(custom_keyboard[0][0], tuple) or isinstance(custom_keyboard[0][0], list):
			def get_data(b):
				s = json.dumps(b[1])
				return s

			keyboard = [[InlineKeyboardButton(b[0], callback_data=get_data(b)) for b in line] for line in
						custom_keyboard]
			reply_markup = InlineKeyboardMarkup(keyboard)
		else:
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False, resize_keyboard=True)

		return sendMessage(reply_markup=reply_markup)

	elif len(text) > 0 or photo != '':
		return sendMessage()

	if picute:
		bot.sendSticker(uid, sticker=picute)


def forward(frm, to, msg_id):
	updater.bot.forwardMessage(frm, to, message_id=msg_id)


# Added argues to queue and then all queue will be added to updater.job_queue
# in managers.usermanager
def call_in(uid, func, time=1, repeat=False, context=None):
	jobs_to_add.append((uid, func, time, repeat, context))


def get_names(uid):
	chat = updater.bot.getChat(uid)

	name = chat.first_name + ((' ' + chat.last_name) if chat.last_name != '' else chat.title)

	return chat.username, name


def get_printed_name(uid):
	usr = users.get_user(uid)
	username, name = usr['nickname'], usr['name']

	if username != '':
		return '[{0}](telegram.me/{1})'.format(name, username)
	else:
		return name
