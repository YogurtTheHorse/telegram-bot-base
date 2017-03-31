from pymongo import MongoClient
from .user_model import get_user_model
from .variables_model import get_variables_model
from .notifications_model import get_notifications_model

import config

client = MongoClient()
database = client[config.BOT_NAME]

users = get_user_model(database)
variables = get_variables_model(database)
notifications = get_notifications_model(database)