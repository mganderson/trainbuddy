from ferris import BasicModel, Model
from google.appengine.ext import ndb

class WebappUser(Model):
    unique_id = ndb.StringProperty(required=True, indexed=True) # TODO: Make this the key, don't autogen key
    email = ndb.StringProperty(indexed=True)
    hashed_password = ndb.IntegerProperty()
    origin_station = ndb.StringProperty(required=True)
    destination_station = ndb.StringProperty(required=True)
