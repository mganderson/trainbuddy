
from app.models.issue import Issue
from app.models.nypl_location import NyplLocation, DashLocation
from app.models.nypl_user import NyplUser
from app.models.cross_ref import XLocationService ,XIssueUser,XUserLocation
from app.models.service import Service
from ferris import Controller, scaffold, route, ndb, messages, route_with, localize
from ferris.components.flash_messages import FlashMessages
from google.appengine.api import memcache, mail, users
from datetime import datetime, timedelta
import json


class ApiService(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (Service)


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



