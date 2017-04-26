from ferris import BasicModel, Model
from google.appengine.ext import ndb
from app.models.stop import Stop
from app.models.trip import Trip
from app.models.route import Route
from datetime import datetime
from pytz import timezone
import urllib
import json
import csv

# NOTE: This function is based largely on the Webhook tutorial
# provided by API.AI at https://docs.api.ai/docs/webhook
def get_weather_json_by_stop_id(stop_id):
	# Get Stop entity and get its latitude and longitude attributes
	stop = Stop.query(Stop.stop_id == stop_id).fetch(1)[0]
	lat = stop.stop_lat
	lon = stop.stop_lon

	# Format query to Yahoo Weather API
	yahoo_weather_query = 'select * from weather.forecast where woeid in (SELECT woeid FROM geo.places WHERE text="({},{})")'.format(lat, lon)
	yahoo_base_url = "https://query.yahooapis.com/v1/public/yql?q="
	yahoo_REST_query = yahoo_base_url + yahoo_weather_query + "&format=json"

	# Send query and get response as JSON
	result = urllib.urlopen(yahoo_REST_query).read()
	data = json.loads(result)

	if data:
		return data
	else:
		return {}
