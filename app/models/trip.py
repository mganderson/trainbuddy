from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class Trip(Model):
    route_id = ndb.IntegerProperty(required=True, indexed=True)
    service_id = ndb.IntegerProperty(required=True, indexed=True)
    trip_id = ndb.IntegerProperty(required=True, indexed=True)
    trip_headsign = ndb.StringProperty(required=True)
    direction_id = ndb.IntegerProperty(required=True, indexed=True)

    # Unnecessary fields in NJT data
    # block_id = ndb.IntegerProperty()
    # shape_id = ndb.IntegerProperty()

    @classmethod
    def upload_trips_to_datastore(cls, csv_filepath):
        with open(csv_filepath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                # skip first row
                if row[0] != 'route_id':
				    route_id_from_csv = int(row[0])
				    service_id_from_csv = int(row[1])
				    trip_id_from_csv = int(row[2])
				    # Strip out extraneous quote marks from CSV values
				    trip_headsign_from_csv = row[3].replace('"','')
				    direction_id_from_csv = int(row[4])
				    # Construct object
				    trip_object = Trip( route_id=route_id_from_csv,
				    					service_id=service_id_from_csv,
				    					trip_id=trip_id_from_csv,
				    					trip_headsign=trip_headsign_from_csv,
				    					direction_id=direction_id_from_csv)
				    trip_object.put()

