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

from app.models.nypl_user import NyplUser ,UserRole


def domain_chain(controller):
    """
    Make sure the active user's email account falls within the accepted domains.
    """      
    return True

# example
@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, domain_chain)


