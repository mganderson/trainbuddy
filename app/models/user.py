from ferris import BasicModel, Model
from google.appengine.ext import ndb

class User(Model):
    # unique_id = ndb.StringProperty(required=True, indexed=True) # TODO: Make this the key, don't autogen key
    origin_station = ndb.StringProperty(required=True)
    destination_station = ndb.StringProperty(required=True)
    slack_id = ndb.StringProperty(indexed=False) # don't need to index, since it will also serve as unique key
    email = ndb.StringProperty(indexed=True)
    hashed_password = ndb.IntegerProperty()

    @classmethod
    def add_slack_user(cls, slack_id_arg, favorite_station_1, favorite_station_2):
    	"""
    	# Use slack_id as ndb key ID in lieu of autogen key id
    	new_key = ndb.Key(cls, slack_id_arg)
    	"""
    	new_key = ndb.Key(cls, slack_id_arg)
    	# Construct new user
    	new_user = cls(id=slack_id_arg, origin_station=favorite_station_1, destination_station=favorite_station_2, slack_id=slack_id_arg)
    	# Update datastore with new user entity
    	new_user.put()

    @classmethod
    def delete_slack_user(cls, slack_id_arg):
    	user = cls.get_by_id(slack_id_arg)
    	user.key.delete()

    @classmethod
    def update_slack_user(cls, slack_id_arg, favorite_station_1, favorite_station_2):
    	user = cls.get_by_id(slack_id_arg)
    	user.origin_station = favorite_station_1
    	user.destination_station = favorite_station_2
    	user.put()