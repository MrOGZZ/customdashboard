from flask import Flask, jsonify

app = Flask(__name__)

# Dummy dashboard data
dummy_dashboard_data = {
    "WebsiteLinkCount": 100,
    "DMCATakedownsSent": 20,
    "DMCATakedownsSuccessful": 15,
    "AmountSaved": 500
}

@app.route('/')
def home():
    return "Hello, this is your Flask backend!"

@app.route('/dashboard')
def get_dashboard_data():
    return jsonify(dummy_dashboard_data)

if __name__ == '__main__':
    app.run(debug=True)
