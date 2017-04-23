from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class Stop(Model):
    stop_id = ndb.IntegerProperty(required=True, indexed=True)
    stop_name = ndb.StringProperty(required=True, indexed=True)

    # Unnecessary fields in NJT data
    # stop_code
    # stop_desc
    # stop_lat
    # stop_lon
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



