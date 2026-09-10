#from src.distance_matrix import parse_cooridnates_text

coordinates = "50.1029, 14.3935\n50.0880, 14.4207\n50.0955, 14.4144"
coordinates_split = coordinates.split('\n')

lats = []
lons = []

for coordinate in coordinates_split:
    lat, lon = coordinate.split(',')
    lats.append(float(lat))
    lons.append(float(lon))
