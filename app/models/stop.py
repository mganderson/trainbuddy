from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class Stop(Model):
    stop_id = ndb.IntegerProperty(required=True, indexed=True)
    stop_name = ndb.StringProperty(required=True, indexed=True)
    stop_lat = ndb.FloatProperty()
    stop_lon = ndb.FloatProperty()

    # Unnecessary fields in NJT data
    # stop_code
    # stop_desc

    # zone_id

    @classmethod
    def upload_stops_to_datastore(cls, csv_filepath):
        with open(csv_filepath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                # skip first row
                if row[0] != 'stop_id':
                    stop_id_from_csv = int(row[0]) 
                    # Strip out extraneous quote marks from CSV values
                    stop_name_from_csv = row[2].replace('"', '')
                    stop_object = Stop(stop_id=stop_id_from_csv, stop_name=stop_name_from_csv)
                    # put() to datastore
                    stop_object.put()

    @classmethod
    def update_stops_with_lat_long(cls, csv_filepath):
        with open(csv_filepath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                # skip first row
                if row[0] != 'stop_id':
                    stop_id_from_csv = int(row[0])
                    current_stop = Stop.query(Stop.stop_id == int(stop_id_from_csv)).fetch(1)[0]
                    if current_stop:
                        current_stop.stop_lat = float(row[4])
                        current_stop.stop_lon = float(row[5])
                        current_stop.put()

    @classmethod 
    def get_station_id_from_station_name(cls, station_name_as_string):
        name_id_dict = cls.get_stop_name_id_dict()
        return name_id_dict.get(station_name_as_string.upper(), 0)

    @classmethod
    def get_stop_name_id_dict(cls):
        return {"30TH ST. PHL.": 1,
                "ABSECON": 2,
                "ALLENDALE": 3,
                "ALLENHURST": 4,
                "ANDERSON STREET": 5,
                "ANNANDALE": 6,
                "ASBURY PARK": 8,
                "ATCO": 9,
                "ATLANTIC CITY": 10,
                "AVENEL": 11,
                "BASKING RIDGE": 12,
                "BAY HEAD": 13,
                "BAY STREET": 14,
                "BELMAR": 15,
                "BERKELEY HEIGHTS": 17,
                "BERNARDSVILLE": 18,
                "BLOOMFIELD": 19,
                "BOONTON": 20,
                "BOUND BROOK": 21,
                "BRADLEY BEACH": 22,
                "BRICK CHURCH": 23,
                "BRIDGEWATER": 24,
                "BROADWAY": 25,
                "CAMPBELL HALL": 26,
                "CHATHAM": 27,
                "CHERRY HILL": 28,
                "CLIFTON": 29,
                "CONVENT": 30,
                "ROSELLE PARK": 31,
                "CRANFORD": 32,
                "DELAWANNA": 33,
                "DENVILLE": 34,
                "DOVER": 35,
                "DUNELLEN": 36,
                "EAST ORANGE": 37,
                "EDISON STATION": 38,
                "EGG HARBOR": 39,
                "ELBERON": 40,
                "ELIZABETH": 41,
                "EMERSON": 42,
                "ESSEX STREET": 43,
                "FANWOOD": 44,
                "FAR HILLS": 45,
                "GARFIELD": 46,
                "GARWOOD": 47,
                "GILLETTE": 48,
                "GLADSTONE": 49,
                "GLEN RIDGE": 50,
                "GLEN ROCK BORO HALL": 51,
                "GLEN ROCK MAIN LINE": 52,
                "HACKETTSTOWN": 54,
                "HAMMONTON": 55,
                "HARRIMAN": 57,
                "HAWTHORNE": 58,
                "HAZLET": 59,
                "HIGH BRIDGE": 60,
                "HIGHLAND AVENUE": 61,
                "HILLSDALE": 62,
                "HOBOKEN": 63,
                "HOHOKUS": 64,
                "KINGSLAND": 66,
                "LAKE HOPATCONG": 67,
                "LEBANON": 68,
                "LINCOLN PARK": 69,
                "LINDEN": 70,
                "LINDENWOLD": 71,
                "LITTLE FALLS": 72,
                "LITTLE SILVER": 73,
                "LONG BRANCH": 74,
                "LYNDHURST": 75,
                "LYONS": 76,
                "MADISON": 77,
                "MAHWAH": 78,
                "MANASQUAN": 79,
                "MAPLEWOOD": 81,
                "METROPARK": 83,
                "METUCHEN": 84,
                "MIDDLETOWN NJ": 85,
                "MIDDLETOWN NY": 86,
                "MILLBURN": 87,
                "MILLINGTON": 88,
                "MONTCLAIR HEIGHTS": 89,
                "MONTVALE": 90,
                "MORRIS PLAINS": 91,
                "MORRISTOWN": 92,
                "MOUNT OLIVE": 93,
                "MOUNT TABOR": 94,
                "MOUNTAIN AVENUE": 95,
                "MOUNTAIN LAKES": 96,
                "MOUNTAIN STATION": 97,
                "MOUNTAIN VIEW": 98,
                "MURRAY HILL": 99,
                "NANUET": 100,
                "NETCONG": 101,
                "NETHERWOOD": 102,
                "NEW BRUNSWICK": 103,
                "NEW PROVIDENCE": 104,
                "NEW YORK PENN STATION": 105,
                "NEWARK BROAD ST": 106,
                "NEWARK PENN STATION": 107,
                "NORTH BRANCH": 108,
                "NORTH ELIZABETH": 109,
                "NEW BRIDGE LANDING": 110,
                "ORADELL": 111,
                "ORANGE": 112,
                "OTISVILLE": 113,
                "PARK RIDGE": 114,
                "PASSAIC": 115,
                "PATERSON": 116,
                "PEAPACK": 117,
                "PEARL RIVER": 118,
                "PERTH AMBOY": 119,
                "PLAINFIELD": 120,
                "PLAUDERVILLE": 121,
                "POINT PLEASANT": 122,
                "PORT JERVIS": 123,
                "PRINCETON": 124,
                "PRINCETON JCT.": 125,
                "RADBURN": 126,
                "RAHWAY": 127,
                "RAMSEY": 128,
                "RARITAN": 129,
                "RED BANK": 130,
                "RIDGEWOOD": 131,
                "RIVER EDGE": 132,
                "RUTHERFORD": 134,
                "SALISBURY MILLS-CORNWALL": 135,
                "SHORT HILLS": 136,
                "SLOATSBURG": 137,
                "SOMERVILLE": 138,
                "SOUTH AMBOY": 139,
                "SOUTH ORANGE": 140,
                "SPRING LAKE": 141,
                "SPRING VALLEY": 142,
                "STIRLING": 143,
                "SUFFERN": 144,
                "SUMMIT": 145,
                "TETERBORO": 146,
                "TOWACO": 147,
                "TRENTON TRANSIT CENTER": 148,
                "TUXEDO": 149,
                "UPPER MONTCLAIR": 150,
                "WALDWICK": 151,
                "WALNUT STREET": 152,
                "WATCHUNG AVENUE": 153,
                "WATSESSING AVENUE": 154,
                "WESTFIELD": 155,
                "WESTWOOD": 156,
                "WHITE HOUSE": 157,
                "WOODBRIDGE": 158,
                "WOODCLIFF LAKE": 159,
                "WOOD-RIDGE": 160,
                "MILITARY PARK LIGHT RAIL STATION": 6900,
                "DAVENPORT AVENUE LIGHT RAIL STATION": 6907,
                "NORFOLK STREET LIGHT RAIL STATION": 6957,
                "PARK AVENUE NEWARK LIGHT RAIL STATION": 6966,
                "WARREN STREET LIGHT RAIL STATION": 6995,
                "WASHINGTON STREET LIGHT RAIL STATION": 6997,
                "PORT IMPERIAL HBLR STATION": 9878,
                "BLOOMFIELD AVENUE LIGHT RAIL STATION": 14984,
                "ORANGE STREET LIGHT RAIL STATION": 14986,
                "LINCOLN HARBOR LIGHT RAIL STATION": 17699,
                "BRANCH BROOK PARK LIGHT RAIL STATION": 26316,
                "PENN STATION LIGHT RAIL DEPARTURE": 26326,
                "HAMILTON": 32905,
                "JERSEY AVE.": 32906,
                "EXCHANGE PLACE LIGHT RAIL STATION": 36994,
                "ESSEX STREET LIGHT RAIL STATION": 36995,
                "MARIN BOULEVARD LIGHT RAIL STATION": 36996,
                "JERSEY AVENUE LIGHT RAIL STATION": 36997,
                "LIBERTY STATE PARK-RIDE LIGHT RAIL STA": 36998,
                "GARFIELD AVENUE LIGHT RAIL STATION": 36999,
                "MLK DRIVE LIGHT RAIL STATION": 37000,
                "WEST SIDE AVENUE LIGHT RAIL STATION": 37001,
                "RICHARD STREET LIGHT RAIL STATION": 37002,
                "DANFORTH AVENUE LIGHT RAIL STATION": 37003,
                "45TH STREET LIGHT RAIL STATION": 37004,
                "34TH STREET LIGHT RAIL STATION": 37005,
                "ABERDEEN-MATAWAN": 37169,
                "HARBORSIDE LIGHT RAIL STATION": 37376,
                "HARSIMUS COVE LIGHT RAIL STATION": 37377,
                "NEWPORT LIGHT RAIL STATION": 37378,
                "NEWARK AIRPORT RAILROAD STATION": 37953,
                "SILVER LAKE LIGHT RAIL STATION": 38064,
                "GROVE STREET LIGHT RAIL STATION": 38065,
                "MSU": 38081,
                "UNION": 38105,
                "FRANK R LAUTENBERG SECAUCUS LOWER LEVEL": 38174,
                "FRANK R LAUTENBERG SECAUCUS UPPER LEVEL": 38187,
                "22ND STREET LIGHT RAIL STATION": 38229,
                "TRENTON TRANSIT CENTER LIGHT RAIL STA": 38291,
                "HAMILTON AVENUE LIGHT RAIL STATION": 38292,
                "CASS STREET LIGHT RAIL STATION": 38293,
                "BORDENTOWN LIGHT RAIL STATION": 38294,
                "ROEBLING LIGHT RAIL STATION": 38295,
                "FLORENCE LIGHT RAIL STATION": 38296,
                "BURLINGTON TOWNE CTR LIGHT RAIL STATION": 38297,
                "BURLINGTON SOUTH LIGHT RAIL STATION": 38298,
                "BEVERLY/EDGEWATER PARK LIGHT RAIL STA": 38299,
                "DELANCO LIGHT RAIL STATION": 38300,
                "RIVERSIDE LIGHT RAIL STATION": 38301,
                "CINNAMINSON LIGHT RAIL STATION": 38302,
                "RIVERTON LIGHT RAIL STATION": 38303,
                "PALMYRA LIGHT RAIL STATION": 38304,
                "ROUTE 73/PENNSAUKEN LIGHT RAIL STATION": 38305,
                "36TH STREET LIGHT RAIL STATION": 38306,
                "WALTER RAND TRANSPORTATION CTR": 38307,
                "COOPER STREET/RUTGERS LIGHT RAIL STATION": 38308,
                "AQUARIUM LIGHT RAIL STATION": 38309,
                "ENTERTAINMENT CENTER LIGHT RAIL STATION": 38310,
                "RAMSEY ROUTE 17 STATION": 38417,
                "2ND STREET LIGHT RAIL STATION": 38441,
                "9TH STREET LIGHT RAIL STATION": 38442,
                "BERGENLINE AVE": 38578,
                "TONNELLE AVENUE LIGHT RAIL STATION": 38579,
                "BROAD STREET LIGHT RAIL STATION": 39130,
                "RIVERFRONT STADIUM LIGHT RAIL STATION": 39131,
                "WASHINGTON PARK LIGHT RAIL STATION": 39132,
                "ATLANTIC STREET LIGHT RAIL STATION": 39133,
                "NJPAC/CENTRE STREET LIGHT RAIL STATION": 39134,
                "HOBOKEN TERMINAL LIGHT RAIL STATION": 39348,
                "MOUNT ARLINGTON": 39472,
                "WAYNE/ROUTE 23 TRANSIT CENTER [RR]": 39635,
                "PENN STATION LIGHT RAIL ARRIVAL": 42545,
                "8TH STREET LIGHT RAIL STATION": 42673,
                "PENNSAUKEN TRANSIT CENTER LIGHT RAIL STA": 43288,
                "PENNSAUKEN TRANSIT CENTER": 43298,
                "WESMONT": 43599}





