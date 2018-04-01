from django.shortcuts import render

from .forms import LocationAForm, LocationBForm, KeywordForm
import requests
import math

API_KEY = 'AIzaSyCDV8b-Ht-AF1LWYjydiKmdWL9KQbygYkc'
# Create your views here.
def index(request):
    if request.method == 'POST':
        formA = LocationAForm(request.POST)
        formB = LocationBForm(request.POST)
        formKey = KeywordForm(request.POST)


        if formA.is_valid() and formB.is_valid() and formKey.is_valid():
            loc_a = formA.cleaned_data['loc_a']
            loc_b = formB.cleaned_data['loc_b']
            keyword = formKey.cleaned_data['keyword']


            locationA = loc_a
            locationB = loc_b

             # create RESTful URL from two locations
            payload = {'origin':locationA, 'destination':locationB, 'key':API_KEY}
            url = 'https://maps.googleapis.com/maps/api/directions/json?'

            # get response from Google Maps Directions API
            search_res = requests.get(url, params=payload)
            search_res.raise_for_status()


            # convert Google response to JSON
            json_result = search_res.json()

            total_distance = json_result['routes'][0]['legs'][0]['distance']['value']
            half_distance = total_distance/2

            steps = get_steps(json_result)
            middle = get_midpoint(half_distance, steps)

            data = get_data(keyword, middle)
            places = get_places(data)

            details = get_details(data)


            return render(request, 'index.html', {
            'formA': formA,
            'formB': formB,
            'formKey': formKey,
            'loc_a': loc_a,
            'loc_b': loc_b,
            'middle': middle,
            'keyword': keyword,
            'places': places,
            'details': details # name, rating, tier
        })
    else:
        formA = LocationAForm()
        formB = LocationBForm()
        formKey = KeywordForm()
        return render(request, 'index.html',{
            'formA': formA,
            'formB': formB,
            'formKey': formKey,
            'loc_a': [34.0170246,-118.4037084],
            'loc_b': [33.8515601,-118.2442366],
            'middle': [33.91095308376905, -118.32861233946454],
            'details': [[0, 5.5, 1], [0, 8, 2], [0, 9.9, 1], [0, 3.2, 3], [0, 6.9, 2]],
            'places': [[33.922260840366064, -118.3272922039032], [33.901649493522804, -118.33360090616722], [33.9163962, -118.3161643], [33.90397159999999, -118.3261131], [33.90217274169682, -118.33114169962998]]
        })





def get_steps(jsonr):
    """Get the steps (distance in meters, startpoint lat&lng, endpoint lat&lng) along route"""
    steps = []
    for step in jsonr['routes'][0]['legs'][0]['steps']:
        steps.append([step['distance']['value'], step['start_location'], step['end_location']])
    return steps

def get_midpoint(half_distance: int, steps: [(int, str, str)]) -> [float, float]:
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

    angle = math.atan(lng_length/lat_length)


    if (startpos[0] < endpos[0]) and (startpos[1] < endpos[1]):
        return (startpos[0]+left_over_distance*math.cos(angle)/110500, startpos[1]+left_over_distance*math.sin(angle)/110500)

    elif (startpos[0] < endpos[0] and startpos[1] > endpos[1]):
        return (startpos[0]+left_over_distance*math.cos(angle)/110500, startpos[1]+left_over_distance*math.sin(angle)/110500)
    return (startpos[0]-left_over_distance*math.cos(angle)/110500, startpos[1]-left_over_distance*math.sin(angle)/110500)

    # if (endpos[0] > startpos[0] and endpos[1] > startpos[1]) or \
    #    (endpos[0] < startpos[0] and endpos[1] > startpos[1]):
    #     return (startpos[0]+left_over_distance*math.cos(angle)/111000, startpos[1]+left_over_distance*math.sin(angle)/111000)
    # return [startpos[0]-left_over_distance*math.cos(angle)/111000, startpos[1]-left_over_distance*math.sin(angle)/111000]


def get_data(search, midpoint):
    url = 'https://api.foursquare.com/v2/venues/explore'

    query = search
    cur_location = str(midpoint)[1:-1]

    params = dict(
        client_id='G15NBKKGLQULJQJ40W2IIW4KNK2YYO23ULFTQI5QSW1DDISP',
        client_secret='OOPKKSDWURQS0R1E5RY3C34OE0DJVTEUSQTRWO1MJDLS0IYF',
        v='20180331',
        ll=cur_location,
        query=query,
        limit=5
    )

    resp = requests.get(url=url, params=params)
    data = resp.json()

    return data


def get_places(data):
    """Return a list of lists containing the latitudes and longitudes of nearby locations"""
    places = []
    for item in data['response']['groups'][0]['items']:
        places.append([item['venue']['location']['lat'],
                       item['venue']['location']['lng']])
    return places

def get_details(data):
    """Return a list of lists containing the details of each location"""
    details = [] # name, rating, tier
    for item in data['response']['groups'][0]['items']:
        details.append([item['venue']['categories'][0]['name'],item['venue']['rating'],item['venue']['price']['tier']])
    return details
