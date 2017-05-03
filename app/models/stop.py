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
    def get_station_name_from_station_id(cls, station_id):
        name_id_dict = cls.get_id_to_stop_name_dict()
        return name_id_dict.get(station_id, 0)

    @classmethod
    def get_id_to_stop_name_dict(cls):
        orig_map = cls.get_stop_name_id_dict()
        inv_map = {v: k for k, v in orig_map.iteritems()}
        return inv_map

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

    @classmethod
    def get_list_of_station_names_all_caps(cls):
        return ["30TH ST. PHL.","ABSECON","ALLENDALE","ALLENHURST","ANDERSON STREET","ANNANDALE","ASBURY PARK","ATCO","ATLANTIC CITY","AVENEL","BASKING RIDGE","BAY HEAD","BAY STREET","BELMAR","BERKELEY HEIGHTS","BERNARDSVILLE","BLOOMFIELD","BOONTON","BOUND BROOK","BRADLEY BEACH","BRICK CHURCH","BRIDGEWATER","BROADWAY","CAMPBELL HALL","CHATHAM","CHERRY HILL","CLIFTON","CONVENT","ROSELLE PARK","CRANFORD","DELAWANNA","DENVILLE","DOVER","DUNELLEN","EAST ORANGE","EDISON STATION","EGG HARBOR","ELBERON","ELIZABETH","EMERSON","ESSEX STREET","FANWOOD","FAR HILLS","GARFIELD","GARWOOD","GILLETTE","GLADSTONE","GLEN RIDGE","GLEN ROCK BORO HALL","GLEN ROCK MAIN LINE","HACKETTSTOWN","HAMMONTON","HARRIMAN","HAWTHORNE","HAZLET","HIGH BRIDGE","HIGHLAND AVENUE","HILLSDALE","HOBOKEN","HOHOKUS","KINGSLAND","LAKE HOPATCONG","LEBANON","LINCOLN PARK","LINDEN","LINDENWOLD","LITTLE FALLS","LITTLE SILVER","LONG BRANCH","LYNDHURST","LYONS","MADISON","MAHWAH","MANASQUAN","MAPLEWOOD","METROPARK","METUCHEN","MIDDLETOWN NJ","MIDDLETOWN NY","MILLBURN","MILLINGTON","MONTCLAIR HEIGHTS","MONTVALE","MORRIS PLAINS","MORRISTOWN","MOUNT OLIVE","MOUNT TABOR","MOUNTAIN AVENUE","MOUNTAIN LAKES","MOUNTAIN STATION","MOUNTAIN VIEW","MURRAY HILL","NANUET","NETCONG","NETHERWOOD","NEW BRUNSWICK","NEW PROVIDENCE","NEW YORK PENN STATION","NEWARK BROAD ST","NEWARK PENN STATION","NORTH BRANCH","NORTH ELIZABETH","NEW BRIDGE LANDING","ORADELL","ORANGE","OTISVILLE","PARK RIDGE","PASSAIC","PATERSON","PEAPACK","PEARL RIVER","PERTH AMBOY","PLAINFIELD","PLAUDERVILLE","POINT PLEASANT","PORT JERVIS","PRINCETON","PRINCETON JCT.","RADBURN","RAHWAY","RAMSEY","RARITAN","RED BANK","RIDGEWOOD","RIVER EDGE","RUTHERFORD","SALISBURY MILLS-CORNWALL","SHORT HILLS","SLOATSBURG","SOMERVILLE","SOUTH AMBOY","SOUTH ORANGE","SPRING LAKE","SPRING VALLEY","STIRLING","SUFFERN","SUMMIT","TETERBORO","TOWACO","TRENTON TRANSIT CENTER","TUXEDO","UPPER MONTCLAIR","WALDWICK","WALNUT STREET","WATCHUNG AVENUE","WATSESSING AVENUE","WESTFIELD","WESTWOOD","WHITE HOUSE","WOODBRIDGE","WOODCLIFF LAKE","WOOD-RIDGE","MILITARY PARK LIGHT RAIL STATION","DAVENPORT AVENUE LIGHT RAIL STATION","NORFOLK STREET LIGHT RAIL STATION","PARK AVENUE NEWARK LIGHT RAIL STATION","WARREN STREET LIGHT RAIL STATION","WASHINGTON STREET LIGHT RAIL STATION","PORT IMPERIAL HBLR STATION","BLOOMFIELD AVENUE LIGHT RAIL STATION","ORANGE STREET LIGHT RAIL STATION","LINCOLN HARBOR LIGHT RAIL STATION","BRANCH BROOK PARK LIGHT RAIL STATION","PENN STATION LIGHT RAIL DEPARTURE","HAMILTON","JERSEY AVE.","EXCHANGE PLACE LIGHT RAIL STATION","ESSEX STREET LIGHT RAIL STATION","MARIN BOULEVARD LIGHT RAIL STATION","JERSEY AVENUE LIGHT RAIL STATION","LIBERTY STATE PARK-RIDE LIGHT RAIL STA","GARFIELD AVENUE LIGHT RAIL STATION","MLK DRIVE LIGHT RAIL STATION","WEST SIDE AVENUE LIGHT RAIL STATION","RICHARD STREET LIGHT RAIL STATION","DANFORTH AVENUE LIGHT RAIL STATION","45TH STREET LIGHT RAIL STATION","34TH STREET LIGHT RAIL STATION","ABERDEEN-MATAWAN","HARBORSIDE LIGHT RAIL STATION","HARSIMUS COVE LIGHT RAIL STATION","NEWPORT LIGHT RAIL STATION","NEWARK AIRPORT RAILROAD STATION","SILVER LAKE LIGHT RAIL STATION","GROVE STREET LIGHT RAIL STATION","MSU","UNION","FRANK R LAUTENBERG SECAUCUS LOWER LEVEL","FRANK R LAUTENBERG SECAUCUS UPPER LEVEL","22ND STREET LIGHT RAIL STATION","TRENTON TRANSIT CENTER LIGHT RAIL STA","HAMILTON AVENUE LIGHT RAIL STATION","CASS STREET LIGHT RAIL STATION","BORDENTOWN LIGHT RAIL STATION","ROEBLING LIGHT RAIL STATION","FLORENCE LIGHT RAIL STATION","BURLINGTON TOWNE CTR LIGHT RAIL STATION","BURLINGTON SOUTH LIGHT RAIL STATION","BEVERLY/EDGEWATER PARK LIGHT RAIL STA","DELANCO LIGHT RAIL STATION","RIVERSIDE LIGHT RAIL STATION","CINNAMINSON LIGHT RAIL STATION","RIVERTON LIGHT RAIL STATION","PALMYRA LIGHT RAIL STATION","ROUTE 73/PENNSAUKEN LIGHT RAIL STATION","36TH STREET LIGHT RAIL STATION","WALTER RAND TRANSPORTATION CTR","COOPER STREET/RUTGERS LIGHT RAIL STATION","AQUARIUM LIGHT RAIL STATION","ENTERTAINMENT CENTER LIGHT RAIL STATION","RAMSEY ROUTE 17 STATION","2ND STREET LIGHT RAIL STATION","9TH STREET LIGHT RAIL STATION","BERGENLINE AVE","TONNELLE AVENUE LIGHT RAIL STATION","BROAD STREET LIGHT RAIL STATION","RIVERFRONT STADIUM LIGHT RAIL STATION","WASHINGTON PARK LIGHT RAIL STATION","ATLANTIC STREET LIGHT RAIL STATION","NJPAC/CENTRE STREET LIGHT RAIL STATION","HOBOKEN TERMINAL LIGHT RAIL STATION","MOUNT ARLINGTON","WAYNE/ROUTE 23 TRANSIT CENTER [RR]","PENN STATION LIGHT RAIL ARRIVAL","8TH STREET LIGHT RAIL STATION","PENNSAUKEN TRANSIT CENTER LIGHT RAIL STA","PENNSAUKEN TRANSIT CENTER","WESMONT"]

    @classmethod
    def get_list_of_station_names_title_case(cls):
        return ["30th St. Phl.","Absecon","Allendale","Allenhurst","Anderson Street","Annandale","Asbury Park","Atco","Atlantic City","Avenel","Basking Ridge","Bay Head","Bay Street","Belmar","Berkeley Heights","Bernardsville","Bloomfield","Boonton","Bound Brook","Bradley Beach","Brick Church","Bridgewater","Broadway","Campbell Hall","Chatham","Cherry Hill","Clifton","Convent","Roselle Park","Cranford","Delawanna","Denville","Dover","Dunellen","East Orange","Edison Station","Egg Harbor","Elberon","Elizabeth","Emerson","Essex Street","Fanwood","Far Hills","Garfield","Garwood","Gillette","Gladstone","Glen Ridge","Glen Rock Boro Hall","Glen Rock Main Line","Hackettstown","Hammonton","Harriman","Hawthorne","Hazlet","High Bridge","Highland Avenue","Hillsdale","Hoboken","Hohokus","Kingsland","Lake Hopatcong","Lebanon","Lincoln Park","Linden","Lindenwold","Little Falls","Little Silver","Long Branch","Lyndhurst","Lyons","Madison","Mahwah","Manasquan","Maplewood","Metropark","Metuchen","Middletown NJ","Middletown NY","Millburn","Millington","Montclair Heights","Montvale","Morris Plains","Morristown","Mount Olive","Mount Tabor","Mountain Avenue","Mountain Lakes","Mountain Station","Mountain View","Murray Hill","Nanuet","Netcong","Netherwood","New Brunswick","New Providence","New York Penn Station","Newark Broad St","Newark Penn Station","North Branch","North Elizabeth","New Bridge Landing","Oradell","Orange","Otisville","Park Ridge","Passaic","Paterson","Peapack","Pearl River","Perth Amboy","Plainfield","Plauderville","Point Pleasant","Port Jervis","Princeton","Princeton Jct.","Radburn","Rahway","Ramsey","Raritan","Red Bank","Ridgewood","River Edge","Rutherford","Salisbury Mills-Cornwall","Short Hills","Sloatsburg","Somerville","South Amboy","South Orange","Spring Lake","Spring Valley","Stirling","Suffern","Summit","Teterboro","Towaco","Trenton Transit Center","Tuxedo","Upper Montclair","Waldwick","Walnut Street","Watchung Avenue","Watsessing Avenue","Westfield","Westwood","White House","Woodbridge","Woodcliff Lake","Wood-ridge","Military Park Light Rail Station","Davenport Avenue Light Rail Station","Norfolk Street Light Rail Station","Park Avenue Newark Light Rail Station","Warren Street Light Rail Station","Washington Street Light Rail Station","Port Imperial Hblr Station","Bloomfield Avenue Light Rail Station","Orange Street Light Rail Station","Lincoln Harbor Light Rail Station","Branch Brook Park Light Rail Station","Penn Station Light Rail Departure","Hamilton","Jersey Ave.","Exchange Place Light Rail Station","Essex Street Light Rail Station","Marin Boulevard Light Rail Station","Jersey Avenue Light Rail Station","Liberty State Park-Ride Light Rail Sta","Garfield Avenue Light Rail Station","MLK Drive Light Rail Station","West Side Avenue Light Rail Station","Richard Street Light Rail Station","Danforth Avenue Light Rail Station","45th Street Light Rail Station","34th Street Light Rail Station","Aberdeen-Matawan","Harborside Light Rail Station","Harsimus Cove Light Rail Station","Newport Light Rail Station","Newark Airport Railroad Station","Silver Lake Light Rail Station","Grove Street Light Rail Station","MSU","Union","Frank R Lautenberg Secaucus Lower Level","Frank R Lautenberg Secaucus Upper Level","22nd Street Light Rail Station","Trenton Transit Center Light Rail Sta","Hamilton Avenue Light Rail Station","Cass Street Light Rail Station","Bordentown Light Rail Station","Roebling Light Rail Station","Florence Light Rail Station","Burlington Towne Ctr Light Rail Station","Burlington South Light Rail Station","Beverly/Edgewater Park Light Rail Sta","Delanco Light Rail Station","Riverside Light Rail Station","Cinnaminson Light Rail Station","Riverton Light Rail Station","Palmyra Light Rail Station","Route 73/Pennsauken Light Rail Station","36th Street Light Rail Station","Walter Rand Transportation Ctr","Cooper Street/Rutgers Light Rail Station","Aquarium Light Rail Station","Entertainment Center Light Rail Station","Ramsey Route 17 Station","2nd Street Light Rail Station","9th Street Light Rail Station","Bergenline Ave","Tonnelle Avenue Light Rail Station","Broad Street Light Rail Station","Riverfront Stadium Light Rail Station","Washington Park Light Rail Station","Atlantic Street Light Rail Station","NJPAC/Centre Street Light Rail Station","Hoboken Terminal Light Rail Station","Mount Arlington","Wayne/Route 23 Transit Center [RR]","Penn Station Light Rail Arrival","8th Street Light Rail Station","Pennsauken Transit Center Light Rail Sta","Pennsauken Transit Center","Wesmont"]










