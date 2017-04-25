from ferris import BasicModel, Model
from google.appengine.ext import ndb
from app.models.stop import Stop
from app.models.trip import Trip
from app.models.route import Route
from app.models.stop_time import StopTime
from datetime import datetime
from pytz import timezone
import csv

class StopTimes(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (StopTime)

    #TODO
    def list(self):
        pass

    #TODO
   def view(self):
        pass
