# ==================================================
# Hack U KOSEN
# このプログラムは
#   国土地理院・指定緊急避難場所データ
#   https://hinan.gsi.go.jp/hinanjocjp/hinanbasho/koukaidate.html
# を用いている。
# ==================================================

import requests
import json
import numpy as np
import pprint as pp
import sys,os

def find_evacuation_point(currentAddress="五稜郭公園", hazardType='03', GPS=None, userID=None):

    print('CALLED find_evacuation_point!')

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [1] get API key
    try:
        from src.findNearestEvacuation.data.APIKEY import APIKEY

    except ModuleNotFoundError:
        returnData = {
            'ErrorCode': 'Google API KEY not found',
        }
        return returnData


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [2] get latitude(N) and longitude(E) of current address FROM JavaScript
    if GPS is None:
        print('ERROR : GPS is None')
        exit()
    else:
        N = float(GPS['N'])
        E = float(GPS['E'])


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [3] load all evacuation points of All from .json data
    try:
        with open('src/findNearestEvacuation/data/mergeFromCity.json', 'r') as f:
            points = json.load(f)
    except FileNotFoundError:
        print('ModuleNotFoundError')
        print('The data/mergeFromCity.json does NOT exist on same directry.')
        exit()


    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # [4] find some evacuation points which can be used for specified disasters and near the current location.
    distlist = []
    hazardTypeName = {
        '03': 'windAndFloodDamage',
        '04': 'windAndFloodDamage',
        '05': 'windAndFloodDamage',
        '33': 'windAndFloodDamage',
        '35': 'windAndFloodDamage',
        '08': 'highTideHazard',
        '38': 'highTideHazard',
        '50': 'earthquakeHazard',
        '60': 'volcanicHazard',
        '70': 'landslideDisaster',

        # '20': 'windAndFloodDamage',
    }
    for key, value in zip(points.keys(), points.values()):
        if (value['hazardTypes'][hazardTypeName[hazardType]]):
            eucD = np.sqrt((float(value['geopoint']['North']) - N)**2 + (float(value['geopoint']['East']) - E)**2) / 0.0090133729745762
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
        + str(N) + ', ' + str(E) + '&destination=' + str(destN) + ', ' + str(destE) + '&mode=walking&key=' + APIKEY

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

    possibleList.sort(key = lambda x: x[4])

    url = 'https://www.google.com/maps/dir/' + str(N) + ',+' + str(E) +\
          '/' + points[possibleList[0][0]]['geopoint']['North'] + ',+' + points[possibleList[0][0]]['geopoint']['East'] + '/'
    returnData = {
        'userID': userID,
        'url': url,
        'ErrorCode': None,
        'EvacuationPoint': points[possibleList[0][0]]['name']
    }

    return returnData