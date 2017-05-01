from app.models.service import Service
from app.models.stop import Stop
from app.models.stop_time import StopTime
from app.models.trip import Trip
from app.models.user import User
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
        This method receives all JSON from API.AI and then calls the appropriate
        method based on the value of the "action" key in the API.AI JSON
        """
        self.meta.change_view('JSON')

        # Get JSON data from POST request sent by API.ai
        json_data = json.loads(self.request.body)

        # Check if user is using Slack by seeing if nested key "source"
        # exists in json_data and whether its value is equal to "slack"
        slack_user = False
        slack_user_id = ""
        try:
            if 'originalRequest' in json_data:
                if 'source' in json_data['originalRequest']:
                    if json_data['originalRequest']['source'].lower() == 'slack':
                        slack_user = True
                        slack_user_id = json_data['originalRequest']['data']['event']['user']

        except Exception as e:
            print "Exception: {}".format(e)

        if slack_user:
            print "Yes, this request is from a slack user! User ID is {}".format(slack_user_id)
        else:
            print "No, this request is NOT from a slack user"
        
        if json_data.get("result").get("action") == "get_the_weather_for_city":
            self.context['data'] = self.get_the_weather_for_city(json_data)
        elif json_data.get("result").get("action") == "praise_colin":
            self.context['data'] = self.praise_colin(json_data)
        elif json_data.get("result").get("action") == "create_profile.create_profile-yes":
            if slack_user:
                self.context['data'] = self.create_profile(json_data, slack_user_id)
            else:
                speech = "Sorry, I can only create accounts for Slack users right now."
                self.context['data'] = self.format_response(speech, speech,{}, [], "")
        elif json_data.get("result").get("action") == "delete_profile.delete_profile-yes":
            if slack_user:
                self.context['data'] = self.delete_profile(json_data, slack_user_id)
            else:
                speech = "Sorry, there's only profile for Slack users at this point, so there's no profile to delete for you."
                self.context['data'] = self.format_response(speech, speech,{}, [], "")
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
        elif json_data.get("result").get("action") == "get_favoritepair_train_time":
            self.context['data'] = self.get_favoritepair_train_time(json_data, slack_user_id)
        elif json_data.get("result").get("action") == "get_weather":
            self.context['data'] = self.get_weather(json_data)
        elif json_data.get("result").get("action") == "get_request_json":
            self.context['data'] = self.format_response(json.dumps(json_data),json.dumps(json_data),{}, [], "")
        else:
            return {}


    ##############################
    # Methods for API.AI webhook #
    ##############################

    def create_profile(self, json_data, slack_id):
        favorite_station_1 = json_data.get("result").get("contexts")[0].get("parameters").get("favorite_station_1")
        favorite_station_2 = json_data.get("result").get("contexts")[0].get("parameters").get("favorite_station_2")
        print 'Value of json_data.get("result").get("parameters"): {}'.format(json_data.get("result").get("parameters"))
        # Check if profile already exists
        existing_user = User.get_by_id(slack_id)
        if existing_user != None:
            speech = "A profile already exists for you.  You can say \"edit profile\" if you'd like to change your station preferences."
            return self.format_response(speech, speech, {}, [], "")
        try:
            print "In create_profile try block | slack_id: {} | favorite_station_1: {} | favorite_station_2: {}".format(slack_id, favorite_station_1, favorite_station_2)
            User.add_slack_user(slack_id, favorite_station_1, favorite_station_2)
            speech = "User profile created successfully!  If you ever want to update or delete it, just say \"edit profile\" or \"delete profile\""
            return self.format_response(speech, speech, {}, [], "")
        except Exception as e:
            print e
            speech = "Uh oh - I suffered some sort of error trying to create your account.  I apologize for the inconvenience."
            return self.format_response(speech, speech, {}, [], "")

    def delete_profile(self, json_data, slack_id):
        existing_user = User.get_by_id(slack_id)
        if existing_user is None:
            speech = "A profile doesn't seem to be saved for you, so there's nothing to delete.  If you'd like to create one at any point, just say \"create profile\""
            return self.format_response(speech, speech, {}, [], "")
        try:
            User.delete_slack_user(slack_id)
            speech = "User profile deleted successfully.  If you ever want to create a new profile just say \"create profile\""
            return self.format_response(speech, speech, {}, [], "")
        except Exception as e:
            print e
            speech = "Uh oh - I suffered some sort of error trying to delete your account.  I apologize for the inconvenience."
            return self.format_response(speech, speech, {}, [], "")

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

    def get_favoritepair_train_time(self, json_data, slack_id):
        # Check if user has a profile saved; if not
        # return an error message
        existing_user = None
        try:
            existing_user = User.get_by_id(slack_id)
        except Exception as e:
            print e
            speech = "I don't seem to have a profile saved with your favorite stations.  You can specify what station(s) you want train information for, or, if you are a Slack user, create a profile by saying \"create profile\""
            return self.format_response(speech, speech, {}, [], "")
        #else:
        favorite_station_1 = existing_user.origin_station
        favorite_station_2 = existing_user.destination_station
        train_from_1_to_2 = StopTime.get_next_stop_time_for_station_to_station(favorite_station_1.upper(), favorite_station_2.upper())
        train_from_2_to_1 = StopTime.get_next_stop_time_for_station_to_station(favorite_station_2.upper(), favorite_station_1.upper())
        if train_from_1_to_2 and train_from_2_to_1:
            speech = "The next departure from {} to {} is the {} {} train.  ".format(  train_from_1_to_2.get("departing_from",""),
                                                                                    favorite_station_2.title(),
                                                                                    train_from_1_to_2.get("pretty_departure_time",""),
                                                                                    train_from_1_to_2.get("route_name","")
                                                                                   )
            speech += "The next departure from {} to {} is the {} {} train".format( train_from_2_to_1.get("departing_from",""),
                                                                                    favorite_station_1.title(),
                                                                                    train_from_2_to_1.get("pretty_departure_time",""),
                                                                                    train_from_2_to_1.get("route_name","")
                                                                                       )
        else:
            speech = "I can't seem to find departures between {} and {}.".format(favorite_station_1.title(), favorite_station_2.title())
        return self.format_response(speech, speech, {}, [], "NJTransit GTFS Static Data")

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

    # Not used anymore
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


    ############################
    #      Helper Methods      #
    ############################


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

    # Test for webhook
    def praise_colin(self, json_data):
        city = json_data.get("result").get("parameters").get("geo-city")
        speech = "ColBol is top cat in {}".format(city)
        return self.format_response(speech, city, {}, [], "NJTransit GTFS Static Data")

    #########################################
    # Methods for generating datastore data #
    #########################################

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




