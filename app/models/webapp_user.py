from ferris import BasicModel, Model
from google.appengine.ext import ndb

class WebappUser(Model):
    email = ndb.StringProperty(required=True, indexed=True)
    hashed_password = ndb.IntegerProperty(required=True)
    favorite_station_1 = ndb.StringProperty(required=True)
    favorite_station_2 = ndb.StringProperty(required=True)

    @classmethod
    def add_webapp_user(cls, email_arg, hashed_password_arg, favorite_station_1_arg, favorite_station_2_arg):
    	# Construct new WebappUser with email as ID
    	new_user = cls(id=email_arg, email=email_arg, hashed_password=hashed_password_arg, favorite_station_1=favorite_station_1_arg, favorite_station_2=favorite_station_2)
    	# Update datastore with new user entity
    	new_user.put()

    @classmethod
    def delete_webapp_user(cls, email):
    	user = cls.get_by_id(email)
    	user.key.delete()

    @classmethod
    def update_webbapp_user_stations(cls, email, favorite_station_1, favorite_station_2):
    	user = cls.get_by_id(email)
    	user.origin_station = favorite_station_1
    	user.destination_station = favorite_station_2
    	user.put()

    @classmethod
    def update_webbapp_user_password(cls, email, hashed_password):
    	user = cls.get_by_id(email)
    	user.origin_station = hashed_password
    	user.put()