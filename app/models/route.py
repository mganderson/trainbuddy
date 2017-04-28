from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class Route(Model):
    route_id = ndb.IntegerProperty(required=True, indexed=True)
    route_long_name = ndb.StringProperty(required=True, indexed=True)
    route_short_name = ndb.StringProperty()
    route_color = ndb.StringProperty()

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

    @classmethod
    def get_route_short_name_from_id_dict(cls):
        return {	1: "ACL",
					2: "MBL",
					3: "MBL",
					4: "HBLR",
					5: "MBCL",
					6: "PJL",
					7: "M&E",
					8: "Gldst",
					9: "NEC",
					10: "NJCL",
					11: "NJCL",
					12: "NLR",
					13: "PVL",
					14: "Dinky",
					15: "RVL",
					16: "RivL" }


    @classmethod
    def get_route_info_dict_from_id(cls):
        return {	1: {"route_long_name": "Atlantic City Rail Line",
        				"route_short_name": "ACL",
        				"route_color": "#005DAA"}
					2: {"route_long_name": "Montclair-Boonton Line",
        				"route_short_name": "MBL",
        				"route_color": "#E66B5B"},
					3: {"route_long_name": "Montclair-Boonton Line",
        				"route_short_name": "MBL",
        				"route_color": "#E66B5B"},
					4: {"route_long_name": "Hudson-Bergen Light Rail",
        				"route_short_name": "HBLR",
        				"route_color": "#000000"},
					5: {"route_long_name": "Main/Bergen County Line",
        				"route_short_name": "MBCL",
        				"route_color": "#FFCF01"},
					6: {"route_long_name": "Port Jervis Line"",
        				"route_short_name": "PJL",
        				"route_color": "#FF7900"},
					7: {"route_long_name": "Morris & Essex Line",
        				"route_short_name": "M&E",
        				"route_color": "#00A94F"},
					8: {"route_long_name": "Gladstone Branch",
        				"route_short_name": "Gldstn",
        				"route_color": "#A2D5AE"},
					9: {"route_long_name": "Northeast Corridor",
        				"route_short_name": "NEC",
        				"route_color": "#EF3E42"},
					10: {"route_long_name": "North Jersey Coast Line",
        				"route_short_name": "NJCL",
        				"route_color": "#00A4E4"},
					11: {"route_long_name": "North Jersey Coast Line",
        				"route_short_name": "NJCL",
        				"route_color": "#00A4E4"},
					12: {"route_long_name": "Newark Light Rail",
        				"route_short_name": "NLR",
        				"route_color": "#000000"},
					13: {"route_long_name": "Pascack Valley Line",
        				"route_short_name": "PVL",
        				"route_color": "#8E258D"},
					14: {"route_long_name": "Princeton Shuttle",
        				"route_short_name": "Dinky",
        				"route_color": "#EF3E42"},
					15: {"route_long_name": "Raritan Valley Line",
        				"route_short_name": "RVL",
        				"route_color": "#FAA634"},
					16: {"route_long_name": "Riverline Light Rail",
        				"route_short_name": "RivL",
        				"route_color": "#000000"} }
