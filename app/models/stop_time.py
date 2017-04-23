from ferris import BasicModel, Model
from google.appengine.ext import ndb
import csv

class StopTime(Model):
    trip_id = ndb.IntegerProperty(required=True, indexed=True)
    arrival_time = ndb.IntegerProperty(required=True, indexed=True)
    departure_time = ndb.IntegerProperty(required=True, indexed=True)
    stop_id = ndb.IntegerProperty(required=True, indexed=True)
    stop_sequence = ndb.IntegerProperty(required=True, indexed=True)
    
    #Unnecessary fields provided in NJT data
    # pickup_type
    # drop_off_type
    # shape_dist_traveled

    @classmethod
    def upload_stop_times_to_datastore(cls, csv_filepath):
        with open(csv_filepath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                # skip first row
                if row[0] != 'trip_id':
                    trip_id_from_csv = int(row[0])
                    """
                    Below: Converts arrival and departure times to
                    to integer values representing seconds since
                    midnight

                    Rationale for not storing as time datatype:
                    NJT uses system where time ranges from 00:00:00
                    to beyond 24:00:00 (e.g. 26:30:00 represents
                    2:00 AM).  This is presumably because the service
                    day runs beyond midnight.  Therefore, it makes most
                    sense to store departure time as seconds that can be
                    added to a datetime for a given day at 12:00 AM.
                    """
                    arrival_time_string = row[1]
                    #print "Arrival time: " + arrival_time_string
                    # Split the string using colon as delimiter
                    # and convert hours and minutes to seconds to
                    # store as ints
                    arrival_hours = int(arrival_time_string.split(':')[0])
                    arrival_minutes = int(arrival_time_string.split(':')[1])
                    #print "Arrival hours: {}".format(arrival_hours)
                    #print "Arrival minutes: {}".format(arrival_minutes)
                    arrival_time_from_csv = arrival_hours*3600 + arrival_minutes*60
                    #print "Arrival time in seconds {}".format(arrival_time_from_csv)

                    departure_time_string = row[2]
                    #print "Departure time: " + departure_time_string
                    # Split the string using colon as delimiter
                    # and convert hours and minutes to seconds to
                    # store as ints
                    departure_hours = int(departure_time_string.split(':')[0])
                    departure_minutes = int(departure_time_string.split(':')[1])
                    #print "Departure hours: {}".format(departure_hours)
                    #print "Departure minutes: {}".format(departure_minutes)
                    departure_time_from_csv = departure_hours*3600 + departure_minutes*60
                    #print "Arrival time in seconds {}".format(departure_time_from_csv)

                    stop_id_from_csv = int(row[3])
                    stop_sequence_from_csv = int(row[4])
                    
                    # Construct object
                    stop_time_object = StopTime(trip_id=trip_id_from_csv,
                                                arrival_time=arrival_time_from_csv,
                                                departure_time=departure_time_from_csv,
                                                stop_id=stop_id_from_csv,
                                                stop_sequence=stop_sequence_from_csv)
                    stop_time_object.put()


 