import requests
from bs4 import BeautifulSoup as bs
import pprint as pp
import json

def initData():
    print('CALLED \'src/getInfoFromJMA/initData.py\'')
    url = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    bs4 = bs(res.text, 'lxml-xml')
    last_w = bs4.select_one('entry > id').text
    # print(last_w)

    url = "https://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    bs4 = bs(res.text, 'lxml-xml')
    last_e = bs4.select_one('entry > id').text
    # print(last_e)

    lastInfoOut = {
        'Warning': last_w,
        'Earthquake': last_e
    }
    with open('src/getInfoFromJMA/data/lastInfo.json', 'w') as f:
        json.dump(lastInfoOut, f, ensure_ascii=True, indent=4, sort_keys=True, separators=(',', ': '))