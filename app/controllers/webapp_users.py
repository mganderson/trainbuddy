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
import hashlib

class WebappUsers(Controller):
    class Meta:
        prefixes = ('cron','api','do',)
        components = (FlashMessages,messages.Messaging,)
        Model = (WebappUser)

    def add(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        self.context["station_list"] = sorted(Stop.get_list_of_station_names_title_case())

    @route
    def login(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        pass

    @route
    def logout(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        self.session["user_logged_in"] = ""
        self.session["email"] = ""
        self.session["favorite_station_1"] = ""
        self.session["favorite_station_2"] = ""
        return self.redirect('/')

    @route
    def confirm_logout(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        pass

    @route
    def manage_profile(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        pass

    @route
    def check_login(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        email = self.request.params["email"]
        raw_password = self.request.params["password"]

        # Hash raw password and update hashed password attribute
        pw_hash = hashlib.md5(raw_password).hexdigest()

        existing_user = list(WebappUser.query(WebappUser.email == email).filter(WebappUser.hashed_password == pw_hash))
        if len(existing_user) > 0:
            self.session["user_logged_in"] = "True"
            self.session["email"] = existing_user[0].email
            self.session["favorite_station_1"] = existing_user[0].favorite_station_1
            self.session["favorite_station_2"] = existing_user[0].favorite_station_2
            message = "You're logged in as {}! Awesome!".format(email)
            return self.redirect("/webapp_users/success?message={}".format(message))
        else:
            error_message = "Invalid email/password combination."
            return self.redirect("/webapp_users/error?error_message={}".format(error_message))

    @route
    def success(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        self.context["message"] = self.request.params["message"]

        self.context["results1"] = StopTime.get_n_many_departures_origin_dest(self.session["favorite_station_1"], self.session["favorite_station_2"], 1)
        self.context["results2"] = StopTime.get_n_many_departures_origin_dest(self.session["favorite_station_2"], self.session["favorite_station_1"], 1)
        self.context["favorite_station_1"] = self.session["favorite_station_1"]
        self.context["favorite_station_2"] = self.session["favorite_station_2"]

    @route
    def error(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        self.context["error_message"] = self.request.params["error_message"]

    @route
    def create_webapp_user(self):
        if "user_logged_in" not in self.session:
            self.session["user_logged_in"] = ""
        email = self.request.params["email"]
        raw_password = self.request.params["password"]
        fav1 = self.request.params["favorite_station_1"]
        fav2 = self.request.params["favorite_station_2"]
        # Check if account already exists for email     
        existing_users = list(WebappUser.query(WebappUser.email == email))
        if len(existing_users) > 0:
            error_message = "Account already exists for email {}.".format(email)
            return self.redirect("/webapp_users/error?error_message={}".format(error_message))

        # Hash raw password and update hashed password attribute
        pw_hash = hashlib.md5(raw_password).hexdigest()

        # Construct a new WebappUser with a tmp password
        user = WebappUser(email=email, hashed_password=pw_hash, favorite_station_1=fav1, favorite_station_2=fav2, is_active=True)

        # Put to datastore
        key = user.put()

        # Set session variables
        self.session["user_logged_in"] = "True"
        self.session["email"] = user.email
        self.session["favorite_station_1"] = user.favorite_station_1
        self.session["favorite_station_2"] = user.favorite_station_2

        self.context["user_logged_in"] = "True"
        self.context["email"] = user.email
        self.context["favorite_station_1"] = user.favorite_station_1
        self.context["favorite_station_2"] = user.favorite_station_2

        message = "Account created for email {}! Wonderful!".format(email)
        return self.redirect("/webapp_users/success?message={}".format(message))