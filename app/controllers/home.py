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

class Home(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (Service)

    @route
    def list(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        print "self.session[\"user_logged_in\"]: {}".format(self.session["user_logged_in"])
        self.context["user_logged_in"] = self.session["user_logged_in"]
        if self.session["user_logged_in"] == "True":
            return self.redirect("/home/logged_in")

    @route
    def logged_in(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        self.context["results1"] = StopTime.get_n_many_departures_origin_dest(self.session["favorite_station_1"], self.session["favorite_station_2"], 1)
        self.context["results2"] = StopTime.get_n_many_departures_origin_dest(self.session["favorite_station_2"], self.session["favorite_station_1"], 1)
        self.context["favorite_station_1"] = self.session["favorite_station_1"]
        self.context["favorite_station_2"] = self.session["favorite_station_2"]

        
