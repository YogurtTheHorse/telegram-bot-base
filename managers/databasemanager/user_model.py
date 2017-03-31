from mongothon import Schema
from mongothon import create_model

user_vars = {
	'uid': {"type": int, "required": True},
	'lang': {"type": str, "default": 'ru'},
	'state': {"type": str},
	'additional_state': {"type": str, 'default': ''},

	'nickname': {'type': str, 'default': ''},
	'name': {'type': str, 'default': ''},

	'is_admin': {'type': bool, 'default': False}
}

user_schema = Schema(user_vars)


def get_user_model(db):
	Users = create_model(user_schema, db['users'])

	@Users.class_method
	def get_user(cls, uid):
		try:
			return cls.find_one({'uid': uid})
		except:
			return {'uid': uid}

	@Users.class_method
	def save_user(cls, usr_dict):
		d = dict()

		for k in user_vars.keys():
			if k in usr_dict:
				d[k] = usr_dict[k]

		if cls.find({'uid': d['uid']}).count() > 0:
			usr = cls.find_one({'uid': d['uid']})
			usr.update(d)
			usr.save()

			return False
		else:
			usr = Users(d)
			usr.save()

			return True

	@Users.class_method
	def sort_by_field(cls, field):
		offsets = cls.collection.distinct(field)

		res = {}
		for offset in offsets:
			res[offset] = [doc['uid'] for doc in cls.find({field: offset}, {'uid': 1})]

		return res

	@Users.class_method
	def get_ids(cls):
		return cls.collection.distinct('uid')

	return Users
