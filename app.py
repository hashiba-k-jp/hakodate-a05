from flask import Flask, render_template, request
from src.findNearestEvacuation.test import test_app
from src.findNearestEvacuation.find_evacuation_point import find_evacuation_point
# from src.getInfoFromJMA.getInfo import getInfo, Entry
from src.getInfoFromJMA.init import init
import pprint as pp

# get data from JMA and run the program each same time.
import initApp

app = Flask(__name__)

@app.route('/location', methods=['GET'])
def get_location_get():
    return render_template('gps_design.html', title='Get Location App')

@app.route('/location', methods=['POST'])
def get_location_post():
    lat = request.form['lat']
    lng = request.form['lng']
    userID = request.form['userID']
    warningCode = request.form['warningCode']
    print(lat, lng, userID, warningCode)
    # currentAddress = None
    # hazardType = <warningCode>
    # GPS = {'N':<lat>, 'E':<lng>}
    # userID = <userID>
    # isTest = False
    test_app()
    notiData = find_evacuation_point(
        currentAddress=None,
        hazardType=warningCode,
        isTest=False,
        GPS={
            'N': lat,
            'E': lng
        },
        userID=userID
    )
    pp.pprint(notiData)
    send_msg_with_line(
        user_id=notiData['userID'],
        msgs=notiData['url'],
    )
    return "completed!"

'''
#LINEユーザにメッセージを送信する関数
def send_msg_with_line(user_id,msgs):
    send_msg = TextSendMessage(text='')
    try:
        line_bot_api = LineBotApi(ACCESS_TOKEN)

        for msg in msgs:
            if DEBUG == True:
                print('SENDING MESSAGE:{}'.format(msg))
            send_msg = TextSendMessage(text=msg)
            line_bot_api.push_message(user_id,send_msg)
    except linebot.exceptions.LineBotApiError as e:
        print(e.error.message)
        print(e.error.details)

    for msg in msgs:
        if DEBUG == True:
            print('SENNDING MESSAGE:{}'.format(msg))

'''

if __name__ == "__main__":
    init()
    app.run(debug=True, host='localhost', port=5001)

