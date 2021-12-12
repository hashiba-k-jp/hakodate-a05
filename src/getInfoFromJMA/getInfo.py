# ------------------------------------------------
# Hack U KOSEN 2021
# HackID : 15
# ------------------------------------------------

import requests
from bs4 import BeautifulSoup as bs
import pprint as pp
import json

def getInfo():
    print('CALLED \'src/getInfoFromJMA/getInfo.py\'')
    isTest = True # add hakodate city and warningCode=20
    isTestData = False # if true, update every time

    # this function dose ...
    # ~ get information from JAM server
    # ~ create list of tareget city codes with code of warning type
    # ~ finally, send the list to LINE NOTIFICATION PROGRAM

    # check the last information
    try:
        with open('src/getInfoFromJMA/data/lastInfo.json', 'r') as f:
            lastInfo  = json.load(f)
    except FileNotFoundError:
        lastInfo = {
            'Warning': '',
            'Earthquake': ''
        }

    ### pp.pprint(lastInfo)

    # THIS CODE IS JUST FOR TEST !!!
    if isTestData:
        lastInfo = {
            'Warning': '',
            'Earthquake': ''
        }

    # weather Warning
    url_w = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
    res_w = requests.get(url_w)
    res_w.encoding = res_w.apparent_encoding
    Bs4_w = bs(res_w.text, 'lxml-xml')
    entries_w = Bs4_w.select('entry')
    infoSetW = [
        {
            'type': 'Warning',
            'title': i.select_one('title').text,
            'url': i.select_one('id').text,
            'author': i.select_one('author > name').text,
            'time': i.select_one('updated').text,
        }
        for i in entries_w
    ]

    # Earthquake and Volcanic
    url_e = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
    res_e = requests.get(url_e)
    res_e.encoding = res_e.apparent_encoding
    Bs4_e = bs(res_e.text, 'lxml-xml')
    entries_e = Bs4_e.select('entry')
    infoSetE = [
        {
            'type': 'Earthquake',
            'title': i.select_one('title').text,
            'url': i.select_one('id').text,
            'author': i.select_one('author > name').text,
            'time': i.select_one('updated').text,
        }
        for i in entries_e
    ]

    noUpdate = True
    infoSet = []
    # only weather warning, just for now
    for info in infoSetW:
        if info['url'] == lastInfo['Warning']:
            break
        else:
            noUpdate = False
            if info['title'] in ['気象特別警報・警報・注意報']:
                infoSet.append(info)
    # no process (earthquake)
    for info in infoSetE:
        if info['url'] == lastInfo['Earthquake']:
            break
        else:
            noUpdate = False
            if info['title'] in ['震源・震度に関する情報']:
                infoSet.append(info)

    if noUpdate:
        print('No Update!')
        return 0

    entries = [
        Entry(
            type = i['type'],
            title = i['title'],
            author = i['author'],
            time = i['time'],
            url = i['url'],
        ) for i in infoSet
    ]

    notificationTagets = []
    data = []
    for entry in entries:
        entry.details()
        data += entry.data

    if isTest:
        data.append({
            'cityCode': '0120200',
            'warningCode': '03',
        })

    pp.pprint(data)
    with open('src/getInfoFromJMA/data/disasterList.json', 'w') as f:
        json.dump(data, f, ensure_ascii=True, indent=4, sort_keys=True, separators=(',', ': '))

    # record the last information
    lastInfoOut = {
        'Warning': infoSetW[0]['url'],
        'Earthquake': infoSetE[0]['url']
    }
    with open('src/getInfoFromJMA/data/lastInfo.json', 'w', encoding='UTF-8') as f:
        json.dump(lastInfoOut, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


class Entry:
    def __init__(self, type, title, author, time, url):
        self.type = type
        self.title = title
        self.url = url
        self.author = author
        self.time = time
        self.data = []

        # USE  03 大雨警報
        # USE  04 洪水警報
        # USE  05 暴風警報
        # USE  08 高潮警報
        # TEST 20 濃霧注意報
        # USE  33 大雨特別警報
        # USE  35 暴風特別警報
        # USE  38 高潮特別警報
        # USE  50 地震 (勝手に定義した番号であって気象庁公式のものではないことに留意)
        '''
        "windAndFloodDamage" 03, 04, 05, 33, 35, 20(TEST)
        "earthquakeHazard"   50
        "tsunamiHazard"      None
        "volcanicHazard"     None
        "highTideHazard"     08, 38
        "landslideDisaster"  None
        '''


    def details(self):
        if self.type == 'Warning':
            res = requests.get(self.url)
            res.encoding = res.apparent_encoding
            Bs4 = bs(res.text, 'lxml-xml')
            items = Bs4.select('Report > Head > Headline > Information[type=\"気象警報・注意報（市町村等）\"] > Item')
            # w stands for Weather
            # c stands for cities
            # These 4 variables do not have been saved in self.
            self.wCodes = [i.select_one('Kind > Code').text for i in items]
            self.cCodes = [i.select_one('Area > Code').text for i in items]
            for wCode, cCode in zip(self.wCodes, self.cCodes):
                if wCode in ['03', '04', '05', '08', '20', '33', '35', '38']:
                    self.data.append({
                        'cityCode': cCode,
                        'warningCode': wCode
                    })
        elif self.type == 'Earthquake':
            res = requests.get(self.url)
            res.encoding = res.apparent_encoding
            Bs4 = bs(res.text, 'lxml-xml')
            # Earthquake (Intensity: 1≤ )
            if self.title == '震源・震度に関する情報':
                code = [i.text for i in Bs4.select('Body > Intensity > Observation > Pref > Area > City > Code')]
                int = [i.text for i in Bs4.select('Body > Intensity > Observation > Pref > Area > City > MaxInt')]
                data = []
                for code, int in zip(code, int):
                    if int in ['1', '2', '3', '4', '5-', '5+', '6-', '6+', '7']:
                        self.data.append({
                            'cityCode': code,
                            'warningCode': '50'
                        })
            elif 0:
                # volcanicHazard
                pass

