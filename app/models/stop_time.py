from ferris import BasicModel, Model
from google.appengine.ext import ndb

class StopTime(Model):
    trip_id = ndb.IntegerProperty(required=True, indexed=True)
    arrival_time = ndb.StringProperty(required=True, indexed=True)
    departure_time = ndb.StringProperty(required=True, indexed=True)
    stop_id = ndb.IntegerProperty(required=True, indexed=True)
    stop_sequence = ndb.IntegerProperty(required=True, indexed=True)
    
    #Unnecessary fields provided in NJT data
    # pickup_type
    # drop_off_type
    # shape_dist_traveled

 