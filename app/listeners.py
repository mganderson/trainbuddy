"""
Central place to store event listeners for your application,
automatically imported at run time.
"""
import logging
from ferris.core.events import on
from ferris import settings
from google.appengine.api import users
from ferris.core import routing
from google.appengine.api import mail, users, urlfetch


def domain_chain(controller):
    """
    Make sure the active user's email account falls within the accepted domains.
    """      
    return True

# example
@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, domain_chain)

@on('controller_before_render')
def before_render(controller):
	try:
		controller.context["user_logged_in"] = controller.session["user_logged_in"]
		controller.context["email"] = controller.session["email"]
		controller.context["favorite_station_1"] = controller.session["favorite_station_1"]
		controller.context["favorite_station_2"] = controller.session["favorite_station_2"]
	except Exception as e:
		print "In before_render() except block | Exception: {}".format(e)
		controller.context["user_logged_in"] = ""
		controller.context["email"] = ""
		controller.context["favorite_station_1"] = ""
		controller.context["favorite_station_2"] = ""

