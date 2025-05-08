import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load politicians data
def load_politicians():
    try:
        with open('data/politicians.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

@app.route('/')
def index():
    politicians = load_politicians()
    return render_template('index.html', politicians=politicians)

@app.route('/politician/<politician_id>')
def politician_detail(politician_id):
    politicians = load_politicians()
    politician = next((p for p in politicians if p['id'] == politician_id), None)
    
    if not politician:
        return "Politician not found", 404
    
    return render_template('politician_detail.html', politician=politician)

@app.route('/api/speeches')
def get_speeches():
    speaker = request.args.get('speaker', '')
    from_date = request.args.get('from_date', '')
    until_date = request.args.get('until_date', '')
    meeting = request.args.get('meeting', '')
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', '1'))
    
    # Call Kokkai API
    url = "https://kokkai.ndl.go.jp/api/1.0/speech"
    params = {
        'recordPacking': 'json',
        'maximumRecords': 10,
        'startRecord': (page - 1) * 10 + 1
    }
    
    if speaker:
        params['speaker'] = speaker
    if from_date:
        params['from'] = from_date
    if until_date:
        params['until'] = until_date
    if meeting:
        params['nameOfMeeting'] = meeting
    if keyword:
        params['any'] = keyword
    
    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/meetings')
def get_meetings():
    from_date = request.args.get('from_date', '')
    until_date = request.args.get('until_date', '')
    name_of_house = request.args.get('name_of_house', '')
    name_of_meeting = request.args.get('name_of_meeting', '')
    page = int(request.args.get('page', '1'))
    
    # Call Kokkai API
    url = "https://kokkai.ndl.go.jp/api/1.0/meeting"
    params = {
        'recordPacking': 'json',
        'maximumRecords': 10,
        'startRecord': (page - 1) * 10 + 1
    }
    
    if from_date:
        params['from'] = from_date
    if until_date:
        params['until'] = until_date
    if name_of_house:
        params['nameOfHouse'] = name_of_house
    if name_of_meeting:
        params['nameOfMeeting'] = name_of_meeting
    
    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
