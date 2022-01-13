from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('13.125.241.131', 27017, username="test", password="test")
db = client.EmotionDairy

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 포스팅 작성시간을 알아야 하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################


@app.route('/')
def home():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/detail')
def main():

    # 자신의 JWT 토큰을 token_receive에 설정
    token_receive = request.cookies.get('mytoken')
    try:

        # 로그인된 jwt 토큰을 디코드하여 payload 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 로그인 정보를 토대로 user_info 설정
        user_info = db.user.find_one({"username": payload['id']})

        # 유저 정보 index.html로 전달
        return render_template('index.html', user_info=user_info)

        # 실패할 경우 login.html로 되돌아감
    except jwt.ExpiredSignatureError:
        return render_template('login.html')


#################################
##  로그인을 위한 API            ##
#################################

##아이디 중복확인 서버
@app.route('/check_dup', methods=['POST'])
def check_dup():

    # username 설정
    username_receive = request.form['username_give']

    # 설정한 username을 DB에서 찾아서 boolean 이용해서 확인
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


##닉네임 중복확인 서버
@app.route('/check_dup2', methods=['POST'])
def check_dup2():

    # nickname 설정
    nickname_receive = request.form['nickname_give']

    # 설정한 nickname을 DB에서 찾아서 boolean 이용해서 확인
    exists = bool(db.user.find_one({'nickname': nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


##회원가입 저장 서버
@app.route('/sign_up/save', methods=['POST'])
def sign_up():

    # username, password 그리고 nickname 등 3개를 받아옴
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    #패스워드 암호화 hash
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    nickname_receive = request.form['nickname_give']

    # doc에 저장
    doc = {
        'username': username_receive,
        'password': password_hash,
        'nickname': nickname_receive,
    }
    # user에 doc 추가
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


##로그인 서버
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

#########################
### index 페이지 api ###
#########################

##포스팅 디비저장
@app.route('/write', methods=['POST'])
def posting():
    # 자신의 JWT 토큰을 token_receive에 설정
    token_receive = request.cookies.get('mytoken')

    try:
        # jwt 토큰을 디코드하여 payload 설정
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 로그인 정보를 토대로 user_info 설정
        user_info = db.user.find_one({'username': payload["id"]})
        # text, data(날짜) 등 2개를 받아옴
        text_receive = request.form['text_give']
        data_receive = request.form['data_give']
        # nickname, text, data, like를 doc에 저장
        # like는 0으로 초기값을 주고 클릭 시 1씩 올라가도록 설정함
        doc = {
            "nickname": user_info['nickname'],
            "text": text_receive,
            "data": data_receive,
            "like": 0
        }
        # wirtes에 doc 추가
        db.writes.insert_one(doc)
        # 작성이 완료되면 "글 저장 성공" 이라는 msg 띄움
        return jsonify({"result": "success", "msg": "글 저장 성공"})

    except (jwt.ExpiredSignature, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


##포스팅 불러오기
@app.route('/posing', methods=['GET'])
def read_diary():
    # 자신의 JWT 토큰을 token_receive에 설정
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # db에서 가져온 자료를 날짜 내림차순으로 정렬, 포스팅카드는 10개만 보이도록 제한
        posts = list(db.writes.find({}).sort("date", -1).limit(10))
        #  db의 모든 자료에 대한 id 형식을 string으로 변환하여 wirtes로 전송
        for post in posts:
            post["_id"] = str(post["_id"])
        return jsonify({"result": "success", "posts": posts})
    except (jwt.ExpiredSignature, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


##포스팅 삭제하기
@app.route('/detail/delete', methods=['POST'])
def deletepost():
    # text를 받아옴
    text_receive = request.form['text_give']
    # writes의 text와 자신이 입력한 text의 값이 동일하다면 삭제
    db.writes.delete_one({'text': text_receive})
    return jsonify({'msg': '삭제 완료!'})


##좋아요
@app.route('/detail/like', methods=['POST'])
def likepost():
    # text를 받아옴
    text_receive = request.form['text_give']
    # writes의 text와 자신이 입력한 text의 값이 동일하다면 target_text로 설정
    target_text = db.writes.find_one({'text': text_receive})
    # target_text의 like doc를 current_like로 설정
    current_like = target_text['like']
    new_like = current_like + 1

    # 어떤 text에 대해서 함수를 실행시켰는지 확인하여 기존 like 값에 +1
    db.writes.update_one({'text': text_receive}, {'$set': {'like': new_like}})

    return jsonify({'msg': '좋아요!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
