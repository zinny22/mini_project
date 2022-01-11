from flask import Flask, render_template, jsonify, request
import hashlib
import datetime
from datetime import datetime, timedelta
import jwt
app = Flask(__name__)

# EC2 IP
from pymongo import MongoClient
client = MongoClient('13.125.241.131', 27017, username="test", password="test")
db = client.EmotionDairy

# JWT관련
SECRET_KEY = 'SPARTA'

## HTML을 주는 부분
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/detail')
def home():
    return render_template('detail.html')

## API 역할을 하는 부분
# 글 작성하기
@app.route('/detail/list', methods=['POST'])
def write_emotion():
    text_recive = request.form['text_give']
    doc = {
        'text': text_recive
    }
    db.emotion.insert_one(doc)

##로그인&회원가입 코드##
## 아이디 중복 확인 서버쪽 코드
@app.route('/sign/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

##로그인 서버
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


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


