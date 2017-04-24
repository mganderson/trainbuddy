import csv, sys

# First command line argument should be filepath
with open(sys.argv[1]) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    headsigns = []
    for row in reader:
        # skip first row
        if row[0] != 'route_id':
            headsign = row[3].title()
            if headsign not in headsigns:
                headsigns.append(headsign)

for headsign in headsigns:
    print headsign + "," + headsign
