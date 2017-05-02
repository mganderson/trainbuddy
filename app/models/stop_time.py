from ferris import BasicModel, Model
from google.appengine.ext import ndb
from app.models.stop import Stop
from app.models.trip import Trip
from app.models.route import Route
from datetime import datetime
from pytz import timezone
import json
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
    def get_stop_times_for_station_id(cls, station_id):
        stop_times = list(StopTime.query(StopTime.stop_id==int(station_id)))
        return stop_times

    @classmethod
    def get_stop_times_for_station_name(cls, station_name_as_string):
        station_id = Stop.get_station_id_from_station_name(station_name_as_string)
        print "STATION ID: {}".format(station_id)
        return StopTime.get_stop_times_for_station_id(station_id)

    @classmethod
    def get_next_stop_time_for_station_name(cls, station_name_as_string):
        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        print now
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the SERVICE day is at 3:48
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600

        print "Seconds_since_midnight: {}".format(seconds_since_midnight)
        
        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string)

        found_a_train_thats_not_terminating = False
        attempt_no = 1
        train = {}
        while not found_a_train_thats_not_terminating and attempt_no < 30:
            # The query will return a list
            result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
            #print result[attempt_no - 1]

            # If there are no results, this means that the last train of the night 
            # has departed the station.  Subtract 24*3600 from seconds_since_midnight 
            # and query again 
            if len(result) == 0:
                seconds_since_midnight -= 24*3600
                result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
                #print result[attempt_no - 1]

            trip = Trip.query(Trip.trip_id == int(result[attempt_no - 1].trip_id)).fetch(1)
            #print trip[0]

            # Check to make sure the trip is not terminating at the 
            # station provided by the user
            if str(trip[0].trip_headsign).lower() != station_name_as_string.lower():
                #Takes departure_time, terminus, departure_from (origin), direction_id
                train = cls.build_train_object(departure_time=result[attempt_no - 1].departure_time, 
                                           terminus=str(trip[0].trip_headsign), departure_from=str(station_name_as_string), 
                                           direction_id=trip[0].direction_id, route_id=trip[0].route_id)
                """
                train = {   "departure_time": result[attempt_no - 1].departure_time,
                            "pretty_departure_time": cls.pretty_format_time(result[attempt_no - 1].departure_time),
                            "terminus": str(trip[0].trip_headsign).title(), # Title case the direction sign
                            "departing_from": str(station_name_as_string).title(),
                            "direction_id": trip[0].direction_id,
                            "route_name": Route.get_route_name_from_id_dict()[trip[0].route_id], # Get route name from route id
                            "user_destination": ""
                }
                """
                found_a_train_thats_not_terminating = True
            # check if we get a result when we subtract 24 hours
            # elif():
            else:
                attempt_no += 1
        return train


##################
# BEGIN NEW WORK #
##################

    # n is the max number of results to return.
    @classmethod
    def get_n_many_departures_for_station(cls, station_name_as_string, n):

        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string)

        stop_time_list = cls.get_x_next_stop_times_by_station_id(station_id, 30)

        # If n is greater than the number of results, set n to number of results
        if n > len(stop_time_list):
            n = len(stop_time_list)

        train_list =[]
        # Iterate over the first n results of the results list and construct train objects
        # for stop_times in stop_time_list
        i = 0
        while len(train_list) < n and i < len(stop_time_list):
            # TODO: determine if weekend run or not
            train_list.append(cls.build_train_object_from_stop_time(stop_time_list[i]))
            i += 1
        return train_list

    # n is the max number of results to return
    @classmethod
    def get_n_many_departures_origin_dest(cls, origin_name_as_string, dest_name_as_string, n):
        # Get station_ids from origin and destination names
        origin_id = Stop.get_station_id_from_station_name(origin_name_as_string)
        dest_id = Stop.get_station_id_from_station_name(dest_name_as_string)

        # get a list of the next 60 departures from the origin station
        stop_time_list = cls.get_x_next_stop_times_by_station_id(origin_id, 60)

        # If n is greater than the number of results, set n to number of results
        if n > len(stop_time_list):
            n = len(stop_time_list)

        train_list =[]
        # Iterate over the first n results of the results list and construct train objects
        # for stop_times in stop_time_list
        i = 0
        while len(train_list) < n and i < len(stop_time_list):
            # TODO: determine if weekend run or not
            # Determine if the train referenced by the stop_time serves the destination station
            if cls.does_trip_serve_station(stop_time_list[i], dest_id):
                train_list.append(cls.build_train_object_from_stop_time(stop_time_list[i]))
            i += 1
        return train_list


##################
#  END NEW WORK  #
##################

    @classmethod
    def get_nth_stop_time_for_station_name(cls, station_name_as_string, n):
        # n is ordinal number for results (e.g. 1 for first train, 2 for second train, etc.)

        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        print now
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the SERVICE day is at 3:48
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600

        print "Seconds_since_midnight: {}".format(seconds_since_midnight)
        
        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string)

        found_a_train_thats_not_terminating = False
        trains_to_skip = n-1 # skip this many successful results to get the nth train
        attempt_no = 1
        train = {}
        while not found_a_train_thats_not_terminating and attempt_no < 30:
            # The query will return a list
            result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
            #print result[attempt_no - 1]

            # If there are no results, this means that the last train of the night 
            # has departed the station.  Subtract 24*3600 from seconds_since_midnight 
            # and query again 
            if len(result) == 0:
                seconds_since_midnight -= 24*3600
                result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
                #print result[attempt_no - 1]

            print "len(result): {}".format(len(result))
            print "attempt_no: {}".format(attempt_no)
            trip = Trip.query(Trip.trip_id == int(result[attempt_no - 1].trip_id)).fetch(1)
            #print trip[0]

            # Check to make sure the trip is not terminating at the 
            # station provided by the user
            if str(trip[0].trip_headsign).lower() != station_name_as_string.lower():
                #Takes departure_time, terminus, departure_from (origin), direction_id
                train = cls.build_train_object(departure_time=result[attempt_no - 1].departure_time, 
                                           terminus=str(trip[0].trip_headsign), departure_from=str(station_name_as_string), 
                                           direction_id=trip[0].direction_id, route_id=trip[0].route_id)
                """
                train = {   "departure_time": result[attempt_no - 1].departure_time,
                            "pretty_departure_time": cls.pretty_format_time(result[attempt_no - 1].departure_time),
                            "terminus": str(trip[0].trip_headsign).title(), # Title case the direction sign
                            "departing_from": str(station_name_as_string).title(),
                            "direction_id": trip[0].direction_id,
                            "route_name": Route.get_route_name_from_id_dict()[trip[0].route_id], # Get route name from route id
                            "user_destination": ""
                }
                """
                if trains_to_skip <= 0:
                    found_a_train_thats_not_terminating = True
                else:
                    trains_to_skip -= 1
                    attempt_no += 1
            # check if we get a result when we subtract 24 hours
            # elif():
            else:
                attempt_no += 1
        return train

    @classmethod
    def get_next_stop_time_for_station_to_station(cls, station_name_as_string1, station_name_as_string2):
        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        print now
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the SERVICE day is at 3:48
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600

        print "Seconds_since_midnight: {}".format(seconds_since_midnight)
        
        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string1)

        found_a_train_thats_going_to_station2 = False
        attempt_no = 1
        train = {}
        while not found_a_train_thats_going_to_station2 and attempt_no < 30:
            # The query will return a list
            result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
            #print result[attempt_no - 1]

            # If there are no results, this means that the last train of the night 
            # has departed the station.  Subtract 24*3600 from seconds_since_midnight 
            # and query again 
            if len(result) == 0:
                seconds_since_midnight -= 24*3600
                result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
                #print result[attempt_no - 1]

            trip = Trip.query(Trip.trip_id == int(result[attempt_no - 1].trip_id)).fetch(1)
            #print trip[0]

            # Check to make sure the train will be stopping at station2:
            # Check if there exists a StopTime entity for the destination
            # station under the same trip_id; if so, check to make sure
            # it that departure_time is AFTER the departure_time of
            # the origin station
            
            #query1 = list(StopTime.query(StopTime.trip_id == trip_id).filter(StopTime.departure_time > result[attempt_no - 1].departure_time))
            query1 = StopTime.query(StopTime.trip_id == trip[0].trip_id)
            query2 = query1.filter(StopTime.stop_id == Stop.get_station_id_from_station_name(station_name_as_string2))
            query3 = query2.filter(StopTime.departure_time > result[attempt_no - 1].departure_time)
            query_result = query3.fetch()
            if len(query_result) == 1:
            #if str(trip[0].trip_headsign).lower() != station_name_as_string.lower():
                #DELETE ME
                #Takes departure_time, terminus, departure_from (origin), direction_id
                train = cls.build_train_object(departure_time=result[attempt_no - 1].departure_time, 
                                           terminus=str(trip[0].trip_headsign), departure_from=str(station_name_as_string1), 
                                           direction_id=trip[0].direction_id, route_id=trip[0].route_id)

                """
                train = {   "departure_time": result[attempt_no - 1].departure_time,
                            "pretty_departure_time": cls.pretty_format_time(result[attempt_no - 1].departure_time),
                            "terminus": str(trip[0].trip_headsign).title(), # Title case the direction sign
                            "departing_from": str(station_name_as_string1).title(),
                            "direction_id": trip[0].direction_id,
                            "route_name": Route.get_route_name_from_id_dict()[trip[0].route_id], # Get route name from route id
                            "user_destination": station_name_as_string2.title()
                }
                """
                found_a_train_thats_going_to_station2 = True
            # check if we get a result when we subtract 24 hours
            # elif():
            else:
                attempt_no += 1
        return train

    @classmethod
    def get_nth_stop_time_for_station_to_station(cls, station_name_as_string1, station_name_as_string2, n):
        # n is ordinal number for results (e.g. 1 for first train, 2 for second train, etc.)

        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        print now
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the SERVICE day is at 3:48
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600

        print "Seconds_since_midnight: {}".format(seconds_since_midnight)
        
        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string1)

        found_a_train_thats_going_to_station2 = False
        trains_to_skip = n - 1
        attempt_no = 1
        train = {}
        while not found_a_train_thats_going_to_station2 and attempt_no < 30:
            # The query will return a list
            result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
            #print result[attempt_no - 1]

            # If there are no results, this means that the last train of the night 
            # has departed the station.  Subtract 24*3600 from seconds_since_midnight 
            # and query again 
            if len(result) == 0:
                seconds_since_midnight -= 24*3600
                result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
                #print result[attempt_no - 1]

            trip = Trip.query(Trip.trip_id == int(result[attempt_no - 1].trip_id)).fetch(1)
            #print trip[0]

            # Check to make sure the train will be stopping at station2
            # TODO:
            # Check if there exists a StopTime entity for the destination
            # station under the same trip_id; if so, check to make sure
            # it that departure_time is AFTER the departure_time of
            # the origin station
            
            #query1 = list(StopTime.query(StopTime.trip_id == trip_id).filter(StopTime.departure_time > result[attempt_no - 1].departure_time))
            query1 = StopTime.query(StopTime.trip_id == trip[0].trip_id)
            query2 = query1.filter(StopTime.stop_id == Stop.get_station_id_from_station_name(station_name_as_string2))
            query3 = query2.filter(StopTime.departure_time > result[attempt_no - 1].departure_time)
            query_result = query3.fetch()
            if len(query_result) == 1:
            #if str(trip[0].trip_headsign).lower() != station_name_as_string.lower():
                #Takes departure_time, terminus, departure_from (origin), direction_id
                train = cls.build_train_object(departure_time=result[attempt_no - 1].departure_time, 
                                           terminus=str(trip[0].trip_headsign), departure_from=str(station_name_as_string1), 
                                           direction_id=trip[0].direction_id, route_id=trip[0].route_id)
                """
                train = {   "departure_time": result[attempt_no - 1].departure_time,
                            "pretty_departure_time": cls.pretty_format_time(result[attempt_no - 1].departure_time),
                            "terminus": str(trip[0].trip_headsign).title(), # Title case the direction sign
                            "departing_from": str(station_name_as_string1).title(),
                            "direction_id": trip[0].direction_id,
                            "route_name": Route.get_route_name_from_id_dict()[trip[0].route_id], # Get route name from route id
                            "user_destination": station_name_as_string2.title()
                }
                """
                if trains_to_skip <= 0:
                    found_a_train_thats_going_to_station2 = True
                else:
                    trains_to_skip -= 1
                    attempt_no += 1
            # check if we get a result when we subtract 24 hours
            # elif():
            else:
                attempt_no += 1
        return train

    @classmethod
    def get_next_stop_time_for_station_name_in_direction(cls, station_name_as_string, direction):
        print "In get_next_stop_time_for_station_name_in_direction()"
        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        print now
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the SERVICE day is at 3:48
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600

        print "Seconds_since_midnight: {}".format(seconds_since_midnight)
        
        # Get station_id from station_name
        station_id = Stop.get_station_id_from_station_name(station_name_as_string)

        found_a_train_thats_not_terminating = False
        attempt_no = 1
        train = {}
        while not found_a_train_thats_not_terminating and attempt_no < 30:
            # The query will return a list
            result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
            print result[attempt_no - 1]

            # If there are no results, this means that the last train of the night 
            # has departed the station.  Subtract 24*3600 from seconds_since_midnight 
            # and query again 
            if len(result) == 0:
                seconds_since_midnight -= 24*3600
                result = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(attempt_no))
                print result[attempt_no - 1]

            trip = Trip.query(Trip.trip_id == int(result[attempt_no - 1].trip_id)).fetch(1)
            print trip[0]

            # Check to make sure the trip is not terminating at the 
            # station provided by the user
            if (str(trip[0].trip_headsign).lower() == direction.lower()):
                #Takes departure_time, terminus, departure_from (origin), direction_id
                train = cls.build_train_object(departure_time=result[attempt_no - 1].departure_time, 
                                           terminus=str(trip[0].trip_headsign), departure_from=str(station_name_as_string), 
                                           direction_id=trip[0].direction_id)
                """
                train = {   "departure_time": result[attempt_no - 1].departure_time,
                            "pretty_departure_time": cls.pretty_format_time(result[attempt_no - 1].departure_time),
                            "terminus": str(trip[0].trip_headsign).title(), # Title case the direction sign
                            "departing_from": str(station_name_as_string).title(),
                            "direction_id": trip[0].direction_id,
                            "route_name": Route.get_route_name_from_id_dict()[trip[0].route_id], # Get route name from route id
                            "user_destination": ""
                }
                """
                found_a_train_thats_not_terminating = True
            else:
                attempt_no += 1
        return train

    @classmethod
    def pretty_format_time(cls, time_as_seconds_after_midnight):
        if time_as_seconds_after_midnight < 12*3600: # If it is the morning
            ampm = "A.M."
        elif time_as_seconds_after_midnight < 24*3600: # If it is after 12:00PM, but before midnight
            time_as_seconds_after_midnight -= 12*3600
            ampm = "P.M."
        else: # If it is after midnight (but the same service day)
            time_as_seconds_after_midnight -= 24*3600
            ampm = "A.M."
        hours = int(time_as_seconds_after_midnight/3600)
        # display 00 as 12:00
        if hours == 0:
            hours = 12
        minutes = int( (time_as_seconds_after_midnight % 3600) / 60 )

        return "{}:{:02d} {}".format(hours,minutes,ampm)

    #Takes departure_time, terminus, departure_from (origin), direction_id
    @classmethod
    def build_train_object(cls, departure_time, terminus, departure_from, direction_id, route_id):
        direction_id = int(direction_id)
        train = {   "departure_time": departure_time,
                    "pretty_departure_time": cls.pretty_format_time(departure_time),
                    "terminus": terminus.title(), # Title case the direction sign
                    "departing_from": departure_from.title(), # Title case the departure station
                    "direction_id": direction_id,
                    "route_id": route_id,
                    "route_name": Route.get_route_info_dict_from_id().get(route_id).get("route_long_name",""),
                    "route_short_name": Route.get_route_info_dict_from_id().get(route_id).get("route_short_name",""),
                    "route_color": Route.get_route_info_dict_from_id().get(route_id).get("route_color",""),
                }
        return train

    #Takes stop_time
    @classmethod
    def build_train_object_from_stop_time(cls, stop_time):
        trip = Trip.query(Trip.trip_id == int(stop_time.trip_id)).fetch(1)
        train = {   "departure_time": stop_time.departure_time,
                    "pretty_departure_time": cls.pretty_format_time(stop_time.departure_time),
                    "terminus": trip[0].trip_headsign.title(), # Title case the direction sign
                    "departing_from": Stop.get_station_name_from_station_id(stop_time.stop_id).title(), # Title case the departure station
                    "direction_id": trip[0].direction_id,
                    "route_id": trip[0].route_id,
                    "route_name": Route.get_route_info_dict_from_id().get(trip[0].route_id).get("route_long_name",""),
                    "route_short_name": Route.get_route_info_dict_from_id().get(trip[0].route_id).get("route_short_name",""),
                    "route_color": Route.get_route_info_dict_from_id().get(trip[0].route_id).get("route_color",""),
                }
        return train

    @classmethod
    def get_seconds_after_midnight(cls):
        # get current local seconds after midnight
        tz = timezone('US/Eastern')
        now = datetime.now(tz)
        seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        """
        First departure of the NJT SERVICE day is at 3:48; prior to that time,
        late-night NJT trains are shown as leaving at times like 
        26:15 (e.g. 2:15 AM).
        So, if seconds less than 3*3600 + 48*60, add 24*3600 to seconds_since_midnight
        so that services after midnight show as being available
        """
        if seconds_since_midnight < 3*3600 + 48*60:
            seconds_since_midnight = seconds_since_midnight + 24*3600
        return seconds_since_midnight

    @classmethod
    def does_trip_serve_station(cls, stop_time, dest_id):
        # Check to make sure the train will be stopping at station:
        # Check if there exists a StopTime entity for the destination
        # station under the same trip_id; if so, check to make sure
        # it that departure_time is AFTER the departure_time of
        # the origin station
        
        query1 = StopTime.query(StopTime.trip_id == stop_time.trip_id)
        query2 = query1.filter(StopTime.stop_id == dest_id)
        query3 = query2.filter(StopTime.departure_time > stop_time.departure_time)
        query_result = query3.fetch()
        if len(query_result) == 1:
            return True
        else:
            return False

    @classmethod
    def get_x_next_stop_times_by_station_id(cls, station_id, x):
        # NOTE: will return a MAX of x departures; may return fewer, so always check len() 
        # of list it returns when iterating over it
        MAX = x

        seconds_since_midnight = cls.get_seconds_after_midnight()
        #print "Seconds_since_midnight: {}".format(seconds_since_midnight)     

        # Get a list of 30 stop times for the given station
        results_list = []
        results_list = list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(MAX))

        # Check if there are no or few results; if so, it may be because the last train of the
        # night has departed.  In this case, subtract a day's worth of seconds from
        # seconds_since_midnight, then search again for stop times and concat results lists
        if len(results_list) < MAX:
            if seconds_since_midnight > 24*3600:
                seconds_since_midnight -= 24*3600
            else:
                seconds_since_midnight = 0
            results_list = results_list + list(StopTime.query(StopTime.stop_id==int(station_id)).filter(StopTime.departure_time > seconds_since_midnight).order(StopTime.departure_time).fetch(MAX-len(results_list)))

        return results_list

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


 