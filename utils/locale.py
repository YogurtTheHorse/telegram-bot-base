import yaml
import random
import config
import logging

loaded_locales = {}
logger = logging.getLogger()

global language
language = config.LANG if hasattr(config, 'LANG') else 'ru'


def get_language():
	global language
	return language


def set_language(lang):
	global language
	language = lang


def get_int_locale(number, code_name, language=None):
	s = get(code_name, language)
	template = '{0} {1}'

	if s is None:
		return s
	else:
		one, two, other = s.split('|')

	if number >= 20:
		num = number % 10
	else:
		num = number

	if num >= 5 or num == 0:
		return template.format(number, other)
	elif num == 1:
		return template.format(number, one)
	elif num >= 2 or num <= 4:
		return template.format(number, two)
	else:
		return template.format(number, other)


def reload():
	loaded_locales.clear()


def get_locale(language=None):
	if language is None:
		language = get_language()

	if language not in loaded_locales:
		loaded_locales[language] = dict()
		try:
			with open('localizations/{0}.yml'.format(language), encoding='utf-8') as lang_file:
				loaded_locales[language] = yaml.load(lang_file)
		except BaseException as e:
			logger.warn(str(e))

	loaded_locales[language]['lang'] = language
	return loaded_locales[language]


def get(code_name, language=None):
	locale = get_locale(language)
	keys = code_name.split('.')

	translation = _get(keys, locale)

	if isinstance(translation, list):
		translation = random.choice(translation)

	if translation is None:
		s = 'Missing string: `{}`, language: `{}`'.format(code_name, locale['lang'])
		logger.warn(s)
		return s

	return translation


def _get(keys, locale):
	head, *tail = keys

	if head in locale:
		new_locale = locale[head]
		if not tail:
			if isinstance(new_locale, str) or isinstance(new_locale, list):
				return new_locale
		else:
			if isinstance(new_locale, object):
				return _get(tail, new_locale)

	return None
