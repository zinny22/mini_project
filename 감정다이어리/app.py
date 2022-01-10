from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('detail.html')

## API 역할을 하는 부분
@app.route('/detail/list', methods=['POST'])
def write_emotion():
    text_recive = request.form['text_give']
    doc = {
        'text': text_recive
    }
    db.emotion.insert_one(doc)



@app.route('/detail/list', methods=['GET'])
def read_diary():
    emotions = list(db.emotion.find({}, {'_id': False}))
    return jsonify({'all_emotions':emotions})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)