from ferris.core import routing, plugins

# Routes all App handlers
routing.auto_route()

# Default root route
routing.redirect('/', to='/helloworld')


# Plugins
#plugins.enable('settings')
#plugins.enable('oauth_manager')
