from ferris import BasicModel, Model
from google.appengine.ext import ndb

class Trip(Model):
    email = ndb.StringProperty(required=True, indexed=True)
    hashed_password = ndb.IntegerProperty(required=True)
    origin_headsign = ndb.StringProperty(required=True)
    destination_station = ndb.StringProperty(required=True, indexed=True)

    # Unnecessary fields in NJT data
    # block_id = ndb.IntegerProperty()
    # shape_id = ndb.IntegerProperty()
