import numpy

def haversine(x: float) -> float:
    return numpy.sin(x/2)**2

def haversine_distance(latitude1_deg: float, longitude1_deg: float, latitude2_deg: float, longitude2_deg: float, radius_km: float = 6378) -> float:
    """
    Calculate distance between two geographical points given in degrees.
    https://en.wikipedia.org/wiki/Haversine_formula 
    """
    latitude1_rad, longitude1_rad, latitude2_rad, longitude2_rad = numpy.radians([
        latitude1_deg,
        longitude1_deg,
        latitude2_deg,
        longitude2_deg])

    latitude_difference = latitude1_rad - latitude2_rad
    longitude_difference = longitude1_rad - longitude2_rad
    
    haversine_theta = haversine(latitude_difference) + numpy.cos(latitude1_rad) * numpy.cos(latitude2_rad) * haversine(longitude_difference)
    distance = 2 * radius_km * numpy.arcsin( numpy.sqrt(haversine_theta) )
    return distance