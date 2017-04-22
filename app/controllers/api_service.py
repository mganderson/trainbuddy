from app.models.service import Service
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

    @route_with()

    @route_with('/api/say_hello')
    def say_hello(self):
        return "HELLO"

    @route_with('/api/get_local_services')
    def api_get_local_services(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')



        try:
            local_services = [{"service_name":service.service_name, "service_id":service.key.urlsafe()} for service in Service.get_all_services()]
            self.context['data'] = {"local_services":local_services}
        except Exception as e:
            self.context['data'] = {"error":e}

    @route_with('/api/webhook')
    def api_webhook(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')

        # Get JSON data from POST request sent by API.ai
        json_data = json.loads(self.request.body)
        my_param = json_data.get("result").get("parameters").get("geo-city")

        
        if json_data.get("result").get("action") == "yahooWeatherForecast":
            self.context['data'] = self.praise_colin(json_data)
        else:
            return {}

        """
        try:
            self.context['data'] = {
                                    "speech": "Col Bol is top cat",
                                    "displayText": "Barack Hussein Obama II is the 44th and current President of the United States, and the first African American to hold the office. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University   and Harvard Law School, where ",
                                    "data": {},
                                    "contextOut": [],
                                    "source": "DuckDuckGo"
                                    }
        except Exception as e:
            self.context['data'] = {"error":e}
        """

    def praise_colin(self, json_data):
        city = json_data.get("result").get("parameters").get("geo-city")
        speech = "ColBol is top cat in {}".format(city)
        return self.format_response(speech, city, {}, [], "NJTransit")


    def format_response(self, speech, displayText, data, contextOut, source):
        data = {
                "speech": speech,
                "displayText": displayText,
                "data": data, #should be a dictionary
                "contextOut": contextOut, #should be a list
                "source": source
                }
        return data


    @route_with('/api/get_local_services')
    def api_get_local_services(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')

        try:
            local_services = [{"service_name":service.service_name, "service_id":service.key.urlsafe()} for service in Service.get_all_services()]
            self.context['data'] = {"local_services":local_services}
        except Exception as e:
            self.context['data'] = {"error":e}


    @route_with('/api/get_local_services_for_location')
    def api_get_local_services_for_location(self):
        """
        This API gets all the local services
        """
        self.meta.change_view('JSON')

        try:
            #Retrieving the JSON payload
            message = self.request.json_body

            data = {}

            if 'location_code' in message:

                if message['location_code'] !="":

                    current_location = DashLocation.get_location_by_location_code(message['location_code'])
                    if len(current_location) > 0:
                        current_location = current_location[0]

                        location_services = [{'service_name':service.service_id.get().service_name} for service in XLocationService.get_services_for_location(current_location.key)]
                        data = {"location_services":location_services}
                    else:
                        data = {"error":"location_code not valid"}
                else:
                    data = {"error":"location_code cannot be empty"}

            else:
                data = {"error":"missing 'location_code'"}

            self.context['data'] = data
        except Exception as e:
            self.context['data'] = {"error":e}

