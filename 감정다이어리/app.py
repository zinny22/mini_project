from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta

## HTML을 주는 부분
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/detail')
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

# 귤 : 감정 이모티콘 부분 추가합니다! db 명칭은 기탁님꺼랑 맞추었습니다!1/11
@app.route('/detail/like', methods=['POST'])
def likepost():
    # sample_receive = request.form['username_give']
    # return jsonify({'msg':'좋아요!'})
    name_receive = request.form['username_give']

    target_name = db.emotion.find_one({'username': name_receive})
    current_like = target_name['like']

    new_like = current_like + 1

    db.emotion.update_one({'username':name_receive},{'$set': {'like': new_like}})

    return jsonify({'msg': '좋아요!'})

@app.route('/detail/sad', methods=['POST'])
def sadpost():
    # sample_receive2 = request.form['sample_give2']
    # return jsonify({'msg':'슬퍼요!'})
    name_receive = request.form['name_give']

    target_name = db.emotion.find_one({'username': name_receive})
    current_sad = target_name['sad']

    new_sad = current_sad + 1

    db.emotion.update_one({'username':name_receive},{'$set': {'sad': new_sad}})

    return jsonify({'msg': '슬퍼요..'})

@app.route('/detail/angry', methods=['POST'])
def angrypost():
    sample_receive3 = request.form['sample_give3']
    print(sample_receive3)
    return jsonify({'msg':'화가 나요!'})
    """
    name_receive = request.form['username_give']

    target_name = db.emotion.find_one({'username': name_receive})
    current_angry = target_name['angry']

    new_angry = current_angry + 1

    db.emotion.update_one({'username':name_receive},{'$set': {'angry': new_angry}})

    return jsonify({'msg': '화가 나요!'})
    """

@app.route('/detail/delete', methods=['POST'])
def deletepost():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg': '삭제되었습니다!'})
    """ 서버 연결시에 이렇게 변경할거에요! 
    username_receive = request.form['username_give']
    db.emotion.delete_one({'username': username_receive})
    return jsonify({'msg': '삭제가 완료되었습니다'})
    """

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


