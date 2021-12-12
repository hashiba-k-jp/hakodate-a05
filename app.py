from flask import Flask, render_template

app = Flask(__name__)


@app.route('/location', methods=['GET'])
def get_location_get():
  return render_template('gps_design.html', title='Get Location App')

if __name__ == "__main__":
    app.run(debug=True)

