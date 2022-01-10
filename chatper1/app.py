from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/api/like', methods=['POST'])
def likepost():
    sample_receive = request.form['sample_give']
    print(sample_receive)
    return jsonify({'msg':'좋아요!'})
    # name_receive = request.form['name_give']
    #
    # target_name = db.ㅇㅇㅇㅇㅇㅇㅇ.find_one({'name': name_receive})
    # current_like = target_name['like']
    #
    # new_like = current_like + 1
    #
    # db.mystar.update_one({'name':name_receive},{'$set': {'like': new_like}})

    # return jsonify({'msg': '좋아요!'})

@app.route('/api/sad', methods=['POST'])
def sadpost():
    sample_receive2 = request.form['sample_give2']
    print(sample_receive2)
    return jsonify({'msg':'슬퍼요!'})

@app.route('/api/angry', methods=['POST'])
def angrypost():
    sample_receive3 = request.form['sample_give3']
    print(sample_receive3)
    return jsonify({'msg':'화가 나요!'})

@app.route('/api/delete', methods=['POST'])
def deletepost():
    sample_receive = request.form['sample_give']
    return jsonify({'msg': '삭제되었습니다!'})
    # username_receive = request.form['username_give']
    # db.ㅇㅇㅇㅇㅇ.delete_many({'username': username_receive})
    #
    # return jsonify({'msg': '삭제가 완료되었습니다'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
