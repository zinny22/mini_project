from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

from pymongo import MongoClient

# client = MongoClient('13.125.241.131', 27017, username="test", password="test")
client = MongoClient('localhost', 27017)
db = client.EmotionDairy

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
# @app.route('/')
# def home():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.user.find_one({"id": payload['id']})
#         return render_template('login.html', nickname=user_info["nick"])
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
#
#
# @app.route('/login')
# def login():
#     msg = request.args.get("msg")
#     return render_template('login.html', msg=msg)


@app.route('/')
def home():
    msg = request.args.get("msg")
    return render_template('login.html',msg=msg)

@app.route('/detail')
def main():

    return render_template('index.html')



#################################
##  로그인을 위한 API            ##
#################################

##아이디 중복확인 서버
@app.route('/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


##닉네임 중복확인 서버
@app.route('/check_dup2', methods=['POST'])
def check_dup2():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.user.find_one({'nickname': nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


##회원가입 저장 서버
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    ##패스워드 암호화 hash
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    nickname_receive = request.form['nickname_give']

    doc = {
        'username': username_receive,
        'password': password_hash,
        'nickname': nickname_receive,
    }

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

    ##이 부분을 넣고 싶은데 실패함##
    # 'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
    # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.

    # except jwt.ExpiredSignatureError:
    # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
    # return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    ##

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    # JWT 토큰에는, payload와 시크릿키가 필요합니다.
    # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.

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


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.
    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


#########################
### index 페이지 api ###
#########################

##포스팅 디비저장
@app.route('/write', methods=['POST'])
def posting():

    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({'username': payload["id"]})
        text_receive = request.form['text_give']
        data_receive = request.form['data_give']

        doc = {
            "nickname": user_info['nickname'],
            "text": text_receive,
            "data": data_receive
        }

        db.writes.insert_one(doc)
        return jsonify({"result":"success", "msg": "글 저장 성공"})

    except (jwt.ExpiredSignature, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


##포스팅 불러오기
@app.route('/write/list', methods=['GET'])
def read_diary():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.writes.find({}).sort("date",-1).limit(10))
        for post in posts:
            post['_id'] =str(post)
        return jsonify({'all_posts':posts})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
