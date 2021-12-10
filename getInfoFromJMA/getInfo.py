# ------------------------------------------------
# Hack U KOSEN 2021
# HackID : 15
# ------------------------------------------------

import requests
from bs4 import BeautifulSoup as bs
import pprint as pp
import json

def getInfo():
    # this function dose ...
    # ~ get information from JAM server
    # ~ create list of tareget city codes with code of warning type
    # ~ finally, send the list to LINE NOTIFICATION PROGRAM

    # check the last information
    try:
        with open('lastInfo.json', 'r') as f:
            lastInfo  = json.load(f)
    except FileNotFoundError:
        lastInfo = {
            'weather': '',
            'earthquake': ''
        }

    # THIS CODE IS JUST FOR TEST !!!
    isTest = True
    if isTest:
        lastInfo = {
            'weather': '',
            'earthquake': ''
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
        if info['url'] == lastInfo['weather']:
            break
        else:
            noUpdate = False
            if info['title'] in ['気象特別警報・警報・注意報']:
                infoSet.append(info)
    # no process (earthquake)
    for info in infoSetE:
        if info['url'] == lastInfo['earthquake']:
            break
        else:
            noUpdate = False
            if info['title'] in ['']:
                infoSet.append(info)

    if noUpdate:
        print('No Update!')
        exit()

    pp.pprint(infoSet)
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
    for entry in entries:
        entry.details()
        pp.pprint(entry.data)

    # record the last information
    lastInfoOut = {
        'weather': infoSetW[0]['url'],
        'earthquake': infoSetE[0]['url']
    }
    with open('lastInfo.json', 'w') as f:
        json.dump(lastInfoOut, f, ensure_ascii=True)


class Entry:
    def __init__(self, type, title, author, time, url):
        self.type = type
        self.title = title
        self.url = url
        self.author = author
        self.time = time
        self.data = []

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
                # 02 暴風雪警報
                # 03 大雨警報
                # 04 洪水警報
                # 05 暴風警報
                # 20 濃霧注意報 (TEST USE ONLY)
                # 32 暴風雪特別警報
                # 33 大雨特別警報
                # 35 暴風特別警報
                if wCode in ['02', '03', '04', '05', '20', '32', '33', '35']:
                    self.data.append({
                        'warningCode': wCode,
                        'cityCode': cCode
                    })
        elif self.type == 'Earthquake':
            pass

            res = requests.get(self.url)
            res.encoding = res.apparent_encoding
            Bs4 = bs(res.text, 'lxml-xml')

            # Earthquake (level: 3≤ )
            if self.title == '震度速報':
                










#
getInfo()
