from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class Route(Model):
    route_id = ndb.IntegerProperty(required=True, indexed=True)
    route_long_name = ndb.StringProperty(required=True, indexed=True)

    @classmethod
    def get_route_name_from_id_dict(cls):
        return {	1: "Atlantic City Rail Line",
					2: "Montclair-Boonton Line",
					3: "Montclair-Boonton Line",
					4: "Hudson-Bergen Light Rail",
					5: "Main/Bergen County Line",
					6: "Port Jervis Line",
					7: "Morris & Essex Line",
					8: "Gladstone Branch",
					9: "Northeast Corridor",
					10: "North Jersey Coast Line",
					11: "North Jersey Coast Line",
					12: "Newark Light Rail",
					13: "Pascack Valley Line",
					14: "Princeton Shuttle",
					15: "Raritan Valley Line",
					16: "Riverline Light Rail" }
