from mongothon import Schema
from mongothon import create_model

notitfication_schema = Schema({
	'time': {'type': float, 'required': True},
	'users': { 'type': list, 'required': True },
	'text': {"type": str, "required": True },
	'photo': {'type': str, 'default': ''}
})

def get_notifications_model(db):
	Notifications = create_model(notitfication_schema, db['notifications'])

	@Notifications.class_method
	def get(cls, limit=1):
		try:
			return [ doc for doc in cls.find({}).sort([('time', 1)]).limit(limit) ]
		except:
			return [ ]

	@Notifications.class_method
	def create(cls, time, users, text, photo=''):
		nofication = Notifications({'time': time, 'users': users, 'text': text, 'photo': photo})
		nofication.save()

	return Notifications