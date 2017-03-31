from telegram.ext.dispatcher import run_async

import jsonpickle
import requests
import logging
import config

TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'

logger = logging.getLogger()

if hasattr(config, 'BOTAN_TOKEN'):
	logger.debug('No botan token specified.')
	enabled = True
else:
	enabled = False


@run_async
def track(uid, args, name='Message'):
	if enabled:
		try:
			dt = jsonpickle.encode(args)
			logger.info(dt)
			r = requests.post(
				TRACK_URL,
				params={"token": config.BOTAN_TOKEN, "uid": uid, "name": name},
				data=dt,
				headers={'Content-type': 'application/json'},
			)
			return r.json()
		except requests.exceptions.Timeout:
			return False
		except (requests.exceptions.RequestException, ValueError) as e:
			logger.warn(e)
			return False
	else:
		return False


@run_async
def shorten_url(url, user_id):
	"""
	Shorten URL for specified user of a bot
	"""
	if enabled:
		try:
			return requests.get(SHORTENER_URL, params={
				'token': config.BOTAN_TOKEN,
				'url': url,
				'user_ids': str(user_id),
			}).text
		except:
			return url
	else:
		return url
