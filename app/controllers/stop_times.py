from app.models.service import Service
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.trip import Trip
from ferris import Controller, scaffold, route, ndb, messages, route_with, localize
from ferris.components.flash_messages import FlashMessages
from google.appengine.api import memcache, mail, users
from datetime import datetime, timedelta
import json
import os
import urllib

class StopTimes(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (StopTime)

    @route
    def list_station_to_station(self):
        origin = self.request.params["origin"]
        destination = self.request.params["destination"]
        num_results = 5 # Can be changed in the future to be responsive to req.
        results = []
        for i in range (1, num_results+1):
            results.append(StopTime.get_nth_stop_time_for_station_to_station(origin, destination, i))
        self.context["results"] = results

    @route
    def list_for_station_name(self):
        origin = self.request.params["origin"]
        num_results = 5 # Can be changed in the future to be responsive to req.
        results = []
        for i in range (1, num_results+1):
            results.append(StopTime.get_nth_stop_time_for_station_name(origin, i))
        self.context["results"] = results

    #TODO
	def view(self):
		pass

