from app.models.service import Service
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.trip import Trip
from app.models.webapp_user import WebappUser
from ferris import Controller, scaffold, route, ndb, messages, route_with, localize
from ferris.components.flash_messages import FlashMessages
from google.appengine.api import memcache, mail, users
from datetime import datetime, timedelta
import json
import os
import urllib

class WebappUsers(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (WebappUser)

    def add(self):
        self.context["station_list"] = sorted(Stop.get_list_of_station_names_title_case())

    @route
    def login(self):
        pass

    @route
    def create_webapp_user(self):
        pass