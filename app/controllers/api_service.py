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



def require_user(controller):
    return True

class ApiService(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (Service)
        authorizations = (require_user,)

    @route_with('/api/say_hello')
    def say_hello(self):
        return "HELLO"

    @route_with('/api/get_stops_by_id')
    def get_stops_by_id(self):
        return str(StopTime.get_stop_times_for_station_id(self.request.params["station_id"]))

    @route_with('/api/get_stops_by_name')
    def get_stops_by_name(self):
        return str(StopTime.get_stop_times_for_station_name(self.request.params["station_name"]))

    @route_with("/api/get_next_train_by_station_name")
    def get_next_train_by_station_name(self):
        return str(StopTime.get_next_stop_time_for_station_name(self.request.params["station_name"]))

    @route_with('/api/generate_stops')
    def generate_stops(self):
        Stop.upload_stops_to_datastore("stops.csv")
        return 200

    @route_with('/api/generate_trips')
    def generate_trips(self):
        filename = self.request.params["filename"] +".csv"
        Trip.upload_trips_to_datastore(filename)
        return 200

    @route_with('/api/generate_stop_times')
    def generate_stop_times(self):
        filename = self.request.params["filename"] +".csv"
        StopTime.upload_stop_times_to_datastore(filename)
        return 200


    @route_with('/api/webhook')
    def api_webhook(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')

        # Get JSON data from POST request sent by API.ai
        json_data = json.loads(self.request.body)
        # my_param = json_data.get("result").get("parameters").get("geo-city")

        
        if json_data.get("result").get("action") == "get_the_weather_for_city":
            self.context['data'] = self.get_the_weather_for_city(json_data)
        elif json_data.get("result").get("action") == "praise_colin":
            self.context['data'] = self.praise_colin(json_data)
        elif json_data.get("result").get("action") == "get_next_train_one_station":
            self.context['data'] = self.get_next_train_one_station(json_data)
        elif json_data.get("result").get("action") == "get_next_train_in_direction":
            self.context['data'] = self.get_next_train_in_direction(json_data)
        elif json_data.get("result").get("action") == "get_next_train_two_stations":
            self.context['data'] = self.get_next_train_two_stations(json_data)
        else:
            return {}


    # Just a test / not core functionality
    def get_the_weather_for_city(self, json_data):
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res


    # Just a test
    def praise_colin(self, json_data):
        city = json_data.get("result").get("parameters").get("geo-city")
        speech = "ColBol is top cat in {}".format(city)
        return self.format_response(speech, city, {}, [], "NJTransit")

    def get_next_train_one_station(self, json_data):
        station = json_data.get("result").get("parameters").get("stations")
        train = StopTime.get_next_stop_time_for_station_name(station.upper())
        if train:
            speech = "The next departure from {} is the {} {} train to {}".format(  train.get("departing_from",""),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name",""),
                                                                                    train.get("terminus","") )
        else:
            speech = "I can't seem to find a departure for that station :'("
        return self.format_response(speech, speech, {}, [], "NJTransit")

    def get_next_train_in_direction(self, json_data):
        station = json_data.get("result").get("parameters").get("stations")
        destination = json_data.get("result").get("parameters").get("destination")
        train = StopTime.get_next_stop_time_for_station_name_in_direction(station.upper(), destination)
        if train:
            speech = "The next departure from {} to {} is the {} {} train".format(  train.get("departing_from",""),
                                                                                    train.get("terminus",""),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name","")
                                                                                   )
        else:
            speech = "I can't seem to find a departure for that station :'("
        return self.format_response(speech, speech, {}, [], "NJTransit")

    def get_next_train_two_stations(self, json_data):
        origin = json_data.get("result").get("parameters").get("origin")
        destination = json_data.get("result").get("parameters").get("destination")
        train = StopTime.get_next_stop_time_for_station_to_station(origin.upper(), destination.upper())
        if train:
            speech = "The next departure from {} to {} is the {} {} train".format(  train.get("departing_from",""),
                                                                                    train.get("user_destination",""),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name","")
                                                                                   )
        else:
            speech = "I can't seem to find a departure for that station combo:'("
        return self.format_response(speech, speech, {}, [], "NJTransit")


    def format_response(self, speech, displayText, data, contextOut, source):

        slack_message = { "text": speech}

        data = {
                "speech": speech,
                "displayText": displayText,
                "data": {"slack": slack_message}, #should be a dictionary
                "contextOut": contextOut, #should be a list
                "source": source
                }
        return data




