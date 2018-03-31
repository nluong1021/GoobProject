import requests
import pprint
import math

API_KEY = 'AIzaSyCDV8b-Ht-AF1LWYjydiKmdWL9KQbygYkc'

try:
    locationA = input('Origin: ')
    locationB = input('Destination: ')

    # create RESTful URL from two locations
    payload = {'origin':locationA, 'destination':locationB, 'key':API_KEY}
    url = 'https://maps.googleapis.com/maps/api/directions/json?'

    # get response from Google Maps Directions API
    search_res = requests.get(url, params=payload)
    search_res.raise_for_status()


    # convert Google response to JSON
    json_result = search_res.json()

except:
    pass

total_distance = json_result['routes'][0]['legs'][0]['distance']['value']
half_distance = total_distance/2

def get_steps(jsonr):
    """Get the steps (distance in meters, startpoint lat&lng, endpoint lat&lng) along route"""
    steps = []
    for step in jsonr['routes'][0]['legs'][0]['steps']:
        steps.append([step['distance']['value'], step['start_location'], step['end_location']])
    return steps

def get_midpoint(half_distance: int, steps: [(int, str, str)]) -> (str, str):
    """Get the latitude and longitude of best approximating midpoint between two locations"""
    cur_distance = 0
    cur_step = 0
    while(cur_distance + steps[cur_step][0] <= half_distance):
        cur_distance += steps[cur_step][0]
        cur_step += 1

    left_over_distance = half_distance - cur_distance

    # lat, lng
    startpos = (steps[cur_step][1]['lat'],steps[cur_step][1]['lng'])
    endpos = (steps[cur_step][2]['lat'],steps[cur_step][2]['lng'])
    lat_length = endpos[0] - startpos[0]
    lng_length = endpos[1] - startpos[1]


    # get angle in radians
    angle = math.atan(lng_length/lat_length)

    if (endpos[0] > startpos[0] and endpos[1] > startpos[1]) or \
       (endpos[0] < startpos[0] and endpos[1] > startpos[1]):
        return (startpos[0]+left_over_distance*math.cos(angle)/111000, startpos[1]+left_over_distance*math.sin(angle)/111000)
    return (startpos[0]-left_over_distance*math.cos(angle)/111000, startpos[1]-left_over_distance*math.sin(angle)/111000)


steps = get_steps(json_result)
print(get_midpoint(half_distance, steps))
