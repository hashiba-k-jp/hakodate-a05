from flask import Flask, render_template, request
from src.findNearestEvacuation.test import test_app
from src.findNearestEvacuation.find_evacuation_point import find_evacuation_point
# from src.getInfoFromJMA.getInfo import getInfo, Entry
from src.getInfoFromJMA.init import init

# get data from JMA and run the program each same time.
### import initApp

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
    text = find_evacuation_point(
        currentAddress=None,
        hazardType=warningCode,
        isTest=False,
        GPS={
            'N': lat,
            'E': lng
        },
        userID=userID
    )
    print(text)

    return "completed!"

if __name__ == "__main__":
    init()
    app.run(debug=True, host='localhost', port=5001)

