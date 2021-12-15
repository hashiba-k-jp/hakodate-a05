# ------------------------------------------------
# Hack U KOSEN 2021
# HackID : 15
# ------------------------------------------------

import requests
from bs4 import BeautifulSoup as bs
import pprint as pp
import json
import sys,os
sys.path.append('.')
from funcs import send_msg_with_line, db_connect
import psycopg2


def getInfo():
    print('CALLED \'src/getInfoFromJMA/getInfo.py\'')
    isTest = False # add hakodate city and warningCode=20

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

    # weather Warning
    if not isTest:
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
                if info['title'] in ['気象特別警報・警報・注意報', '土砂災害警戒情報']:
                    infoSet.append(info)
        # no process (earthquake)
        for info in infoSetE:
            if info['url'] == lastInfo['Earthquake']:
                break
            else:
                noUpdate = False
                if info['title'] in ['震源・震度に関する情報', '噴火警報・予報']:
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

    else:
        data = []
        data.append({
            'cityCode': '0120200',
            'warningCode': '03',
        })

    pp.pprint(data)
    # connect to database
    try:
        conn = db_connect()
        cursor = conn.cursor()
        userUrlAllWarning = []
        for d in data:
            # 与えられたcityCode(d['cityCode'])を持つユーザ(user_id)を全て抽出する
            # sql = "SELECT user_id FROM public.user WHERE id = ( SELECT user_id FROM public.resistration WHERE area_id = {});".format(d['cityCode'])
            sql = "SELECT user_id FROM public.resistration WHERE area_id = {};".format(d['cityCode'])
            if isTest:
                print('SQL EXECUTE:{}'.format(sql))
            cursor.execute(sql)
            user_ids = cursor.fetchall()
            user_ids = [i[0] for i in user_ids]

            all_user_ids = []

            for user_id in user_ids:
                sql = "SELECT user_id FROM public.user WHERE id = {};".format(user_id)
                if isTest:
                    print('SQL EXECUTE:{}'.format(sql))
                cursor.execute(sql)
                user_ids = cursor.fetchall()
                user_ids = [i[0] for i in user_ids]
                all_user_ids += user_ids

            pp.pprint(all_user_ids)

            conn.commit()
            userUrl = [{'userid':userid, 'warningCode':d['warningCode']} for userid in all_user_ids]
            userUrlAllWarning += userUrl

        # disconnect to database
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(e.pgerror)
        print(e.diag.message_primary)

    pp.pprint(userUrlAllWarning)

    # send "get information" url to each users
    for user_url in userUrlAllWarning:
        send_msg_with_line(
            user_id=user_url['userid'],
            msgs=["https://{}/location?userID={}&warningCode={}".format(os.environ.get('ROOT_URL'),user_url['userid'], user_url['warningCode'])]
        )

    if not isTest:
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
        # TEST 20 濃霧注意報 -> No USE in the TEST
        # USE  33 大雨特別警報
        # USE  35 暴風特別警報
        # USE  38 高潮特別警報
        # USE  50 地震 (勝手に定義した番号であって気象庁公式のものではないことに留意)
        # USE  70 土砂災害 (同様に勝手に定義)
        '''
        "windAndFloodDamage" 03, 04, 05, 33, 35, 20(TEST)
        "earthquakeHazard"   50
        "tsunamiHazard"      None
        "volcanicHazard"     None
        "highTideHazard"     08, 38
        "landslideDisaster"  70
        '''

    def details(self):
        res = requests.get(self.url)
        res.encoding = res.apparent_encoding
        Bs4 = bs(res.text, 'lxml-xml')
        if self.type == 'Warning':
            if self.title == '気象特別警報・警報・注意報':
                items = Bs4.select('Report > Head > Headline > Information[type=\"気象警報・注意報（市町村等）\"] > Item')
                # w stands for Weather
                # c stands for cities
                # These 4 variables do not have been saved in self.
                self.wCodes = [i.select_one('Kind > Code').text for i in items]
                self.cCodes = [i.select_one('Area > Code').text for i in items]
                for wCode, cCode in zip(self.wCodes, self.cCodes):
                    if wCode in ['03', '04', '05', '08', '33', '35', '38']:
                        self.data.append({
                            'cityCode': cCode,
                            'warningCode': wCode
                        })
            elif self.title == '土砂災害警戒情報':
                items = Bs4.select('Report > Body > warning[type=\"土砂災害警戒情報\"] > Item')
                for item in items:
                    code = item.select_one('Kind > Code').text
                    if code == '3':
                        cCode = item.select_one('Area > Code').text
                        self.data.append({
                            'cityCode': cCode,
                            'warningCode': '70'
                        })
        elif self.type == 'Earthquake':
            # Earthquake (Intensity: 5+≤ )
            if self.title == '震源・震度に関する情報':
                code = [i.text for i in Bs4.select('Body > Intensity > Observation > Pref > Area > City > Code')]
                int = [i.text for i in Bs4.select('Body > Intensity > Observation > Pref > Area > City > MaxInt')]
                data = []
                for code, int in zip(code, int):
                    if int in ['5+', '6-', '6+', '7']:
                        self.data.append({
                            'cityCode': code,
                            'warningCode': '50'
                        })
            elif self.title == '噴火警報・予報':
                # volcanicHazard
                pass