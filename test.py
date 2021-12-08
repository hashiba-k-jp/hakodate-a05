# ==================================================
# Hack U KOSEN
# ==================================================

import requests
import json
import numpy as np
import pprint as pp

try:
    from APIKEY import APIKEY
except ModuleNotFoundError:
    print('ModuleNotFoundError')
    print('The APIKEY.py does NOT exist on same directry.')
    exit()

def find_all_evacuation_point(currentAddress="札幌駅", hazardType='windAndFloodDamage', key=None):

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [1] get current address by google api without GPS
    ## url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + KEY
    ## response = requests.get(url)
    ## response.encoding = response.apparent_encoding
    # This API returns [404]. The reason is not sure, but we can NOT use this API.


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [2] get latitude(N) and longitude(E) of current address
    # -> Everyone can NOT run this program without this API key.
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + currentAddress + '&key=' + KEY
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    if response.status_code != 200:
        print('ERROR : Requests process has NOT successfully finishied at process [2] (get current location)')
        print('URL : {}'.format(url))
        exit()
    data = response.json()
    ### pp.pprint(data)
    N, E = data['results'][0]['geometry']['location']['lat'], data['results'][0]['geometry']['location']['lng']
    # N <class 'float'> := latitude of current location (North)
    # E <class 'float'> := longitude of current location (East)


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [3] load all evacuation points of Hokkaido from .json data
    # THIS FILE IS NOT ON THE GitHUb BECAUSE OF LICENSE PROBLEMS.
    try:
        with open('P20-12_01.json', 'r') as f:
            points = json.load(f)
    except FileNotFoundError:
        print('ModuleNotFoundError')
        print('The P20-12_01.json does NOT exist on same directry.')
        exit()


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [4] find some evacuation points which can be used for specified disasters and near the current location.
    distlist = []
    # hazardType <class 'str'> := type of hazard (disaster) and can be below 6 values
    # -> 'earthquakeHazard', 'notSpecified', 'other', 'tsunamiHazard', 'volcanicHazard', 'windAndFloodDamage'
    for key, value in zip(points.keys(), points.values()):
        if (value['hazardTypes']['notSpecified'] == True) or (value['hazardTypes']['windAndFloodDamage']):
            eucD = np.sqrt((value['geopoint']['North'] - N)**2 + (value['geopoint']['East'] - E)**2) / 0.0090133729745762
            # EUClidean Distance
            distlist.append([key, eucD, value['name']])
    distlist.sort(key = lambda x: x[1])

    # find ALL evacuation point which is less than 0.5 km in a straight line from current location, ...
    ELD = 0.5 # Evacuation Limit Distance
    # or if NO points are in 0.5 km, find 10 points in order of distance.
    listNum = 10
    if len([x for x in distlist if x[1] < ELD]) < listNum:
        possibleList = distlist[:listNum]
    else:
        possibleList = [x for x in distlist if x[1] < ELD]
    # possibleList <class 'list'> := some evacuation points which satisfy [4]


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [5] get walking distances for all points got in [4], and sort them by walking time
    for point in possibleList:
        pointID = point[0]
        destN, destE = points[pointID]['geopoint']['North'], points[pointID]['geopoint']['East']

        url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' \
        + str(N) + ', ' + str(E) + '&destination=' + str(destN) + ', ' + str(destE) + '&mode=walking&key=' + KEY

        response = requests.get(url)
        response.encoding = response.apparent_encoding
        if response.status_code != 200:
            print('ERROR : Requests process has NOT successfully finishied at process [5] (get walking distance)')
            print('URL : {}'.format(url))
            exit()

        data = response.json()
        distMeter = data['routes'][0]['legs'][0]['distance']['value']
        distTime  = data['routes'][0]['legs'][0]['duration']['value']
        point.append(distMeter)
        point.append(distTime)

    print('current address is {}'.format(currentAddress))
    print('tareget hazard is {}'.format(hazardType))
    print('id, name, Euclidean_Dist(km), distance(m), walking time(sec)')
    possibleList.sort(key = lambda x: x[4])
    pp.pprint(possibleList)


# This is for the TEST run
if __name__ == '__main__':
    CA = 'JR Kushiro Station'
    HT = 'tsunamiHazard'
    KEY = APIKEY
    # THIS KEY IS HIDDEN BECAUSE OF PROBLEMS ON SECURITY!
    find_all_evacuation_point(currentAddress=CA, hazardType=HT, key=KEY)
