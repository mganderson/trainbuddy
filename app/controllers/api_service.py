from app.models.service import Service
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.trip import Trip
from weather import get_weather_json_by_stop_id
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

    # Determine which action is being passed in the JSON from API.AI
    # and call the matching method
    @route_with('/api/webhook')
    def api_webhook(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')

        # Get JSON data from POST request sent by API.ai
        json_data = json.loads(self.request.body)
        
        if json_data.get("result").get("action") == "get_the_weather_for_city":
            self.context['data'] = self.get_the_weather_for_city(json_data)
        elif json_data.get("result").get("action") == "praise_colin":
            self.context['data'] = self.praise_colin(json_data)
        elif json_data.get("result").get("action") == "get_next_train_one_station":
            self.context['data'] = self.get_next_train_one_station(json_data)
        elif json_data.get("result").get("action") == "get_next_train_one_station.get_next_train_one_station-towards":
            self.context['data'] = self.get_next_train_one_station_towards(json_data)
        elif json_data.get("result").get("action") == "get_next_train_one_station.get_next_train_one_station-next":
            self.context['data'] = self.get_next_train_one_station_next(json_data)
        elif json_data.get("result").get("action") == "get_next_train_in_direction":
            self.context['data'] = self.get_next_train_in_direction(json_data)
        elif json_data.get("result").get("action") == "get_next_train_two_stations":
            self.context['data'] = self.get_next_train_two_stations(json_data)
        elif json_data.get("result").get("action") == "get_next_train_two_stations.get_next_train_two_stations-next":
            self.context['data'] = self.get_next_train_two_stations_next(json_data)
        elif json_data.get("result").get("action") == "get_weather":
            self.context['data'] = self.get_weather(json_data)
        elif json_data.get("result").get("action") == "get_request_json":
            self.context['data'] = self.format_response(json.dumps(json_data),json.dumps(json_data),{}, [], "")
        else:
            return {}

    ############################
    # Methods for testing only #
    ############################

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

    ###################################
    # END of Methods for testing only #
    ###################################

    # Don't expose this unless needed
    # @route_with('/api/generate_stops')
    def generate_stops(self):
        Stop.upload_stops_to_datastore("stops.csv")
        return 200

    # Don't expose this unless needed
    # @route_with('/api/update_stops_with_lat_lon')
    def update_stops_with_lat_lon(self):
        Stop.update_stops_with_lat_long("stops.csv")
        return 200

    # Don't expose this unless needed
    # @route_with('/api/generate_trips')
    def generate_trips(self):
        filename = self.request.params["filename"] +".csv"
        Trip.upload_trips_to_datastore(filename)
        return 200

     # Don't expose this unless needed
    # @route_with('/api/generate_stop_times')
    def generate_stop_times(self):
        filename = self.request.params["filename"] +".csv"
        StopTime.upload_stop_times_to_datastore(filename)
        return 200

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
        return self.format_response(speech, city, {}, [], "NJTransit GTFS Static Data")

    ##############################
    # Methods for API.AI webhook #
    ##############################
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
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

    def get_next_train_one_station_towards(self, json_data):
        origin = json_data.get("result").get("contexts")[0].get("parameters").get("stations")
        destination = json_data.get("result").get("contexts")[0].get("parameters").get("destination")
        train = StopTime.get_next_stop_time_for_station_to_station(origin.upper(), destination.upper())
        if train:
            speech = "The next departure from {} to {} is the {} {} train".format(  train.get("departing_from",""),
                                                                                    destination.title(),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name","")
                                                                                   )
        else:
            speech = "I can't seem to find a departure for that station combo:'("
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

    def get_next_train_one_station_next(self, json_data):
        station = json_data.get("result").get("contexts")[0].get("parameters").get("stations")
        train = StopTime.get_nth_stop_time_for_station_name(station.upper(), 2)
        if train:
            speech = "The departure after that from {} is the {} {} train to {}".format(train.get("departing_from",""),
                                                                                        train.get("pretty_departure_time",""),
                                                                                        train.get("route_name",""),
                                                                                        train.get("terminus","") )
        else:
            speech = "I can't seem to find a departure for that station :'("
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

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
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

    def get_next_train_two_stations(self, json_data):
        origin = json_data.get("result").get("parameters").get("origin")
        destination = json_data.get("result").get("parameters").get("destination")
        train = StopTime.get_next_stop_time_for_station_to_station(origin.upper(), destination.upper())
        if train:
            speech = "The next departure from {} to {} is the {} {} train".format(  train.get("departing_from",""),
                                                                                    destination.title(),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name","")
                                                                                   )
        else:
            speech = "I can't seem to find a departure for that station combo:'("
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

    def get_next_train_two_stations_next(self, json_data):
        origin = json_data.get("result").get("contexts")[0].get("parameters").get("origin")
        destination = json_data.get("result").get("contexts")[0].get("parameters").get("destination")
        train = StopTime.get_nth_stop_time_for_station_to_station(origin.upper(), destination.upper(), 2)
        if train:
            speech = "The next departure from {} to {} is the {} {} train".format(  train.get("departing_from",""),
                                                                                    destination.title(),
                                                                                    train.get("pretty_departure_time",""),
                                                                                    train.get("route_name","")
                                                                                   )
        else:
            speech = "I can't seem to find a departure for that station combo:'("
        return self.format_response(speech, speech, {}, [], "NJTransit")

    def get_weather(self, json_data):
        stop = json_data.get("result").get("parameters").get("stations")
        stop_id = Stop.get_station_id_from_station_name(stop)
        weather = get_weather_json_by_stop_id(stop_id)
        if weather:
            try:
                city = weather.get("query").get("results").get("channel").get("location").get("city")
                description = weather.get("query").get("results").get("channel").get("item").get("condition").get("text").lower()
                temp = weather.get("query").get("results").get("channel").get("item").get("condition").get("temp")
                units = weather.get("query").get("results").get("channel").get("units").get("temperature")
                speech = "Currently, it's {} {} and {} in {}".format(temp,
                                                                    units,
                                                                    description,
                                                                    city)
            except:
                speech = "The weather service seems to have crapped out.  I'm sorry :'("
        else:
            speech = "The weather service seems to have crapped out.  I'm sorry :'("

        return self.format_response(speech, speech, {}, [], "Yahoo Weather")

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





