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
        self.context["results"] = StopTime.get_n_many_departures_origin_dest(self.request.params["origin"], self.request.params["dest"], 10)
        self.context["origin"] = self.request.params["origin"].title()
        self.context["destination"] = self.request.params["dest"].title()

    @route
    def list_for_station_name(self):
        self.context["results"] = StopTime.get_n_many_departures_for_station(self.request.params["origin"], 10)
        self.context["origin"] = self.request.params["origin"].title()


    #TODO
	def view(self):
		pass

