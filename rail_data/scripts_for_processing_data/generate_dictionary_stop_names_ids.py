import csv

print "{"
with open("stops.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        # skip first row
        if row[0] != 'stop_id':
            stop_id_from_csv = int(row[0]) 
            # Strip out extraneous quote marks from CSV values
            stop_name_from_csv = row[2]
            print "{}: {},".format(stop_name_from_csv, stop_id_from_csv)
print "}"
