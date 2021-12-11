import pprint as pp
import csv
import json

def csvToJson():
    table = []
    with open('mergeFromCity.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            table.append(row)
    '''
        0 市町村コード
        1 市町村名
        2 NO
        3 施設場所名
        4 住所
        5 洪水
        6 崖崩れ/土石流及び地滑り
        7 高潮
        8 地震
        9 津波
        10 大規模な火事
        11 内水氾濫
        12 火山現象
        13 指定避難所との重複
        14 緯度
        15 経度
        16 備考
    '''
    list = {}
    for row in table[2:]:
        list[row[0]+'-'+row[2]] = {
            'address': row[4],
            'geopoint': {
                'East': row[15],
                'North': row[14]
            },
            'hazardTypes': {
                "windAndFloodDamage": row[5] == '1',
                "earthquakeHazard": row[8] == '1',
                "tsunamiHazard": row[9] == '1',
                "volcanicHazard": row[12] == '1',
                "highTideHazard": row[7] == '1',
                "landslideDisaster": row[6] == '1'
            },
            'name': row[3],
        }

    with open('mergeFromCity.json', 'w') as f:
        json.dump(list, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))
    ### pp.pprint(list)

csvToJson()