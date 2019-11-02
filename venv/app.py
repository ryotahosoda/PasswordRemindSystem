import os
import csv
import system as sys
import time
from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)
app.config.from_object(__name__)

counter = {}
# counterの初期化　temppassは判定時に入力した仮のパスワード
with open('./data/userlist.csv', 'r') as f:
    reader = csv.reader(f, lineterminator='\n')
    next(reader)
    for row in reader:
        if row[0] == '':
            pass
        else:
            counter[row[0]] = {'cert': 0, 'exp': 0, 'temppass': ''}


@app.route('/')
def index():
    return render_template('index.html', results={})


@app.route('/start')
def start():
    return render_template('form.html', results={})


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html', results={}, registered=False)
    elif request.method == 'POST':
        r = request.form
        if r['username'] == '' or r['password'] == '':
            # 登録情報不足
            return render_template('register.html', results={'name': r['username'], 'exits': False}, registered=False)
        else:
            if sys.exits_user(r['username']):
                # 二重登録防止
                return render_template('register.html', results={'name': r['username'], 'exits': True},
                                       registered=False)
            else:
                # 登録処理
                sys.write_userlist(r['username'], r['password'])
                sys.log_register(r['username'], r['password'])
                # カウンターの初期化
                global counter
                counter[r['username']] = {'cert': 0, 'exp': 0}
                return render_template('register.html', results={}, registered=True)


@app.route('/confirmation', methods=['POST', 'GET'])
def confirmation():
    if request.method == 'GET':
        return render_template('user_confirm.html', results={'exits': False})
    elif request.method == 'POST':
        r = request.form
        if sys.exits_user(r['username']):
            global counter
            counter[r['username']]['exp'] += 1
            return render_template('user_confirm.html', results={'exits': True}, username=r['username'], flag=0)
        elif r['username'] == '':
            # 空白の時注意を表示　
            return render_template('user_confirm.html', results={'exits': False}, flag=1)
        else:
            # 間違っているユーザー名の時注意を表示　
            return render_template('user_confirm.html', results={'exits': False}, flag=2)


@app.route('/certification/<username>', methods=['POST', 'GET'])
def certification(username):
    global counter
    if request.method == 'GET':
        if counter[username]['cert'] == 0:
            sys.log_start_login(username, counter[username]['exp'])
        return render_template('certification.html', username=username)
    elif request.method == 'POST':
        r = request.form
        # パスワード認証処理
        # 認証回数のカウント
        counter[username]['cert'] += 1
        if sys.certificate(username, r['password'], counter[username]['cert']):
            counter[username]['cert'] = 0
            return render_template('result.html', result='success')
        else:
            if r['password'] == '':
                # 空白入力を登録しない　
                counter[username]['cert'] -= 1
                return render_template('certification.html', username=username, msg='空白になっています')
            elif counter[username]['cert'] != 3:
                # 予備実験は5,本実験は3に変更
                return render_template('result.html', result='again', username=username)
            else:
                # 3回目の認証失敗,本人判定へ
                # 失敗した時もカウントを0に初期化　
                counter[username]['cert'] = 0
                return render_template('result.html', result='failure', username=username)


# counter[username]['cert']をリマインドでも利用するために０で初期化、分けたほうがいい？
@app.route('/judgement/<username>', methods=['POST', 'GET'])
def judgement(username):
    global counter
    if request.method == 'GET':
        return render_template('judgement.html', username=username)
    elif request.method == 'POST':
        r = request.form
        # 判定
        judge = sys.judgement(username, r['password'],1)
        if judge == True:
            # 認証成功
            counter[username]['cert'] = 0
            return render_template('result.html', result='success')
        else:
            if r['password'] == '':
                # 空白入力を登録しない
                return render_template('judgement.html', username=username, msg='空白になっています')
            elif judge == 'judge_success':
                # 本人判定成功
                # 部分的忘却のパスワードを保存
                counter[username]['cert'] = 0
                counter[username]['temppass'] = r['password']
                return render_template('result.html', result='judge_success', username=username)
            else:
                # 本人判定失敗
                counter[username]['cert'] = 0
                return render_template('result.html', result='judge_failure', username=username)


@app.route('/remind/<username>', methods=['POST', 'GET'])
def remind(username):
    global counter
    if request.method == 'GET':
        r = request.form
        hintpw = sys.hint(counter[username]['temppass'], sys.get_password(username))
        count = sys.count(hintpw)
        type = sys.hint_type(count)
        enpw=counter[username]['temppass']
        # type 1:挿入　2;削除　3:置換　4:挿入+置換　5:削除+置換
        return render_template('remind.html', username=username, type=type, insert=count[1], delete=count[2], pw=''.join(hintpw), enpw=enpw)
    elif request.method == 'POST':
        r = request.form
        # パスワード認証処理(ヒントありリマインド)
        # 認証回数のカウント
        counter[username]['cert'] += 1
        if sys.remind(username, r['password'], counter[username]['cert']):
            # リマインド成功
            counter[username]['cert'] = 0
            return render_template('result.html', result='remind_success', pw=sys.get_password(username))
        else:
            if r['password'] == '':
                # 空白入力を登録しない　
                counter[username]['cert'] -= 1
                return render_template('remind.html', username=username)
            elif counter[username]['cert'] != 3:
                counter[username]['temppass'] = r['password']
                return render_template('result.html', result='remind_again', username=username)
            else:
                # 3回目のリマインド失敗
                # 失敗した時もカウントを0に初期化,入力パスワードも初期化
                counter[username]['cert'] = 0
                counter[username]['temppass'] = ''
                return render_template('result.html', result='remind_failure', username=username, pw=sys.get_password(username))


if __name__ == '__main__':
    app.run()
