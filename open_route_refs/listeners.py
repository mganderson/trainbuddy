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
    if controller.route.prefix == 'api':
        return True
    
    elif controller.route.prefix == 'cron':
        return True
    
    else:
        user = users.get_current_user()
        if not user:
            return (controller.redirect(users.create_logout_url('/')))
        
        email_domain = user.email().split('@')[1]    
        if not email_domain in ('nypl.org', 'bookops.org'):
            return False, "You are not authorized to access this site."
        
        return True

# example
@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, domain_chain)


#@on('controller_before_render')
#def before_render(controller):
#    if controller.route.prefix != 'api':
#        pass
        
        

@on('controller_before_render')
def before_render(controller): 
    if controller.route.prefix != 'api':
        current_user = users.get_current_user()
        current_user = current_user.email()       

        userroles = UserRole.get_role_for_user(current_user)


        userprofile = NyplUser.get_user_by_email(current_user)
        myrole =  ""
        mypic =  ""
        for item in userprofile:
            mypic = item.photo_url
        for item in userroles:
            myrole = str(item.role)

        controller.context['active_user_specs'] = userprofile
        controller.context['myrole'] = myrole
        controller.context['active_user_specs3'] = len(userroles)    






