import xml.etree.ElementTree as ET
import pprint as pp
import numpy as np
from bs4 import BeautifulSoup
import json

with open('P20-12_01_GML/P20-12_01.xml', 'r') as f:
    xmldata = f.read()

soup = BeautifulSoup(xmldata, 'xml')

soup_ids = soup.select('Point')
point_names = soup.select('EvacuationFacilities')
### pp.pprint(point_ids)

points = {}



### pp.pprint(soup.text)
### exit()



for i in soup_ids:
    ### print('-' * 25 + i['gml:id'][2:] + '-' * 25)
    n, e = i.find('gml:pos').text.split()
    points[i['gml:id'][2:]] = {'geopoint': {'North':float(n), 'East':float(e)}}

### print('\n\n' + '='*100 + '\n\n')
for i in point_names:
    ### print('-' * 25 + i['gml:id'][4:] + '-' * 25)
    ### pp.pprint(i.select_one('name').text)
    points[i['gml:id'][4:]]['name'] = i.select_one('name').text
    points[i['gml:id'][4:]]['address'] = i.select_one('address').text
    points[i['gml:id'][4:]]['facilityType'] = i.select_one('facilityType').text
    points[i['gml:id'][4:]]['hazardTypes'] = {}
    if i.select_one('earthquakeHazard').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['earthquakeHazard'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['earthquakeHazard'] = False
    if i.select_one('tsunamiHazard').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['tsunamiHazard'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['tsunamiHazard'] = False
    if i.select_one('windAndFloodDamage').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['windAndFloodDamage'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['windAndFloodDamage'] = False
    if i.select_one('volcanicHazard').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['volcanicHazard'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['volcanicHazard'] = False
    if i.select_one('other').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['other'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['other'] = False
    if i.select_one('notSpecified').text == 'true':
        points[i['gml:id'][4:]]['hazardTypes']['notSpecified'] = True
    else:
        points[i['gml:id'][4:]]['hazardTypes']['notSpecified'] = False



jsondata = json.dumps(points, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
with open('P20-12_01.json', 'w', encoding='UTF-8') as f:
    f.write(jsondata)





    #
