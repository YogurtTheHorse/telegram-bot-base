import os
import time
import json
import config
import logging
import datetime

import utils.telegram
import utils.locale
import utils.botan

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Job
from telegram.ext.dispatcher import run_async

from managers import usermanager
from managers import notificationsmanager
from managers.databasemanager import variables

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

if hasattr(config, 'use_files') and config.use_files:
	if not os.path.exists('logs'):
		os.makedirs('logs')

	fileHandler = logging.FileHandler("logs/log_{0}.log".format(time.time()))
	fileHandler.setFormatter(logFormatter)
	logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

utils.telegram.updater = Updater(config.BOT_TOKEN, workers=4)


@run_async
def start(bot, update):
	chat_id = update.message.chat_id
	usermanager.start(chat_id, chat_id in config.ADMINS)
	utils.botan.track(chat_id, update.message, 'New user')


@run_async
def get(bot, update):
	chat_id = update.message.chat_id
	if chat_id not in config.ADMINS:
		utils.telegram.send(chat_id, 'No')
	else:
		bot.send_document(chat_id, document=open('localizations/ru.yml', 'rb'))


@run_async
def msg(bot, update):
	chat_id = update.message.chat_id

	banned = variables.get('banned', [])

	if str(chat_id) in banned or update.message.from_user.username in banned:
		return

	if chat_id in config.ADMINS and update.message.reply_to_message is not None:
		forward_to = update.message.reply_to_message.forward_from.id
		question = update.message.reply_to_message.text
		utils.telegram.send(forward_to, 'Ваше сообщение: {0}\n\nНаш ответ\n{1}'.format(question, update.message.text))
	elif update.message.document is not None:
		if chat_id in config.ADMINS:
			data = bot.getFile(update.message.document.file_id)
			mime = update.message.document.mime_type
			if mime in ['application/x-yaml', 'application/octet-stream']:
				utils.telegram.send(chat_id, 'loading.')

				@run_async
				def anon():
					utils.telegram.send(chat_id, 'locale')
					data.download('localizations/ru.yml')
					utils.locale.reload()
					utils.telegram.send(chat_id, 'loaded.')

				anon()
			else:
				utils.telegram.send(chat_id, 'Unsupprted MIME: {0}'.format(mime))
		else:
			utils.telegram.send(chat_id, 'no.')
	else:
		utils.botan.track(chat_id, update.message)

		if update.message.chat.type == 'private':
			usermanager.msg(chat_id, update)
		else:
			utils.telegram.send(chat_id, 'NOT IMPLEMENTED')
			bot.leaveChat(chat_id)


def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))


def command(foo):
	def handler(bot, update):
		if update.message.chat_id in config.ADMINS:
			foo(bot, update)
		else:
			utils.telegram.send(update.message.chat_id, 'Not admin.')

	return handler


def banlist(bot, update):
	utils.telegram.send(update.message.chat_id, '\n'.join(variables.get('banned', [])))


def ban(bot, update):
	c = variables.get('banned', [])

	name = update.message.text.split()[1]
	if name.startswith('@'):
		name = name[1:]
	utils.telegram.send(update.message.chat_id, name)
	name = str(name)

	if name in c:
		c.remove(name)
	else:
		c.append(name)

	variables.set('banned', c)


@run_async
def inline_button(bot, update):
	query = update.callback_query
	msg_id = query.message.message_id
	chat_id = query.message.chat_id

	try:
		content = json.loads(query.data)
	except ValueError:
		error(bot, update, 'Error loading inline callback data')
	except Exception as e:
		error(bot, update, e)
	else:
		usermanager.inline_button(chat_id, msg_id, content)


def main():
	dp = utils.telegram.updater.dispatcher

	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('ban', command(ban)))
	dp.add_handler(CommandHandler('banlist', command(banlist)))
	dp.add_handler(CommandHandler('get', get))

	dp.add_handler(CallbackQueryHandler(inline_button))
	dp.add_handler(MessageHandler(False, msg))
	dp.add_error_handler(error)

	jq = utils.telegram.updater.job_queue
	jq.put(Job(notificationsmanager.test,
			interval=datetime.timedelta(minutes=1),
			repeat=True,
			context=0), 0)

	utils.telegram.updater.start_polling()
	utils.telegram.updater.idle()

print(123)
if __name__ == '__main__':
	main()
