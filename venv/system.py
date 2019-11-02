import csv
import datetime as dt
import os
import Levenshtein as Lev
from typing import Tuple, List

dict = {'m': 'match', 'i': 'insertion', 'd': 'deletion', 'r': 'replacement'}


# ユーザーリストを記述
def write_userlist(username, password):
    filepath = './data/userlist.csv'
    if os.path.exists(filepath):
        with open(filepath, 'a') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow([username, password])
    else:
        with open(filepath, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['Username', 'Password'])
            w.writerow([username, password])


# タイムスタンプ付きでメッセージを記述する
def write_msg(username, msg, time=''):
    filepath = './data/' + username + '.txt'
    if time == '':
        time = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    text = time + '\t' + msg + '\n'
    with open(filepath, mode='a') as f:
        f.write(text)


# 登録時のログ
def log_register(username, password):
    msg = 'Register User ID: %s, Password: %s' % (username, password)
    write_msg(username, msg)
    write_line(username)


# ログイン試行スタート時のログ
def log_start_login(username, count):
    msg = '%s login attempt' % count_str(count)
    write_msg(username, msg)


# ログイン成功時のログ
def log_success(username, count):
    msg = '%s login succeeded' % count_str(count)
    write_msg(username, msg)
    write_line(username)

# ログイン成功(本人判定)時のログ
def log_j_success(username, count):
    msg = '%s login succeeded(in judgement)' % count_str(count)
    write_msg(username, msg)
    write_line(username)


# ログイン失敗時のログ
def log_failure(username, password, count):
    msg = '%s login failed. password => %s' % (count_str(count), password)
    write_msg(username, msg)


# 　本人判定成功のログ
def log_judgement_success(username, password, resemblance):
    msg = 'judgement succeeded. password => %s, resemblance => %3f' % (password, resemblance)
    write_msg(username, msg)


# 　本人判定失敗のログ
def log_judgement_failure(username, password, resemblance):
    msg = 'judgement failed. password => %s, resemblance => %3f' % (password, resemblance)
    write_msg(username, msg)
    write_line(username)


# リマインド成功時のログ
def log_remind_success(username, count, resemblance):
    msg = '%s remind succeeded, resemblance => %3f' % (count_str(count), resemblance)
    write_msg(username, msg)
    write_line(username)


# リマインド失敗時のログ
def log_remind_failure(username, password, count, resemblance):
    msg = '%s remind failed. password => %s, resemblance => %3f' % (count_str(count), password, resemblance)
    write_msg(username, msg)
    if count == 3:
        write_line(username)


# ラインを記述
def write_line(username):
    filepath = './data/' + username + '.txt'
    with open(filepath, mode='a') as f:
        f.write('====================\n')


# ユーティリティ
def count_str(count):
    cnt_str = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']
    return str(count) + cnt_str[count % 10]


# ユーザーリスト確認
def exits_user(username):
    if os.path.exists('./data/userlist.csv'):
        with open('./data/userlist.csv', 'r') as f:
            reader = csv.reader(f, lineterminator='\n')
            next(reader)
            for row in reader:
                if row[0] == username:
                    return True
    return False


# パスワードチェック
def check_password(username, password):
    return password == get_password(username)


# 　類似度(標準化済)
def resemblance(username, password):
    truepass = get_password(username)
    l = Lev.distance(password, truepass)
    if len(password) >= len(truepass):
        return l / len(password)
    else:
        return l / len(truepass)


# 認証処理
def certificate(username, password, count):
    if check_password(username, password):
        log_success(username, count)
        return True
    else:
        if password == '':
            # 空白を登録しない
            return False
        else:
            log_failure(username, password, count)
            return False


# 本人判定
def judgement(username, password, count):
    # 閾値 3文字まで巨頭
    threshold = 0.25
    if check_password(username, password):
        log_j_success(username, count)
        return True
    else:
        res = resemblance(username, password)
        # 本人判定成功
        if res <= threshold:
            log_judgement_success(username, password, res)
            return 'judge_success'
        # 本人判定失敗
        else:
            log_judgement_failure(username, password, res)
            return 'judge_failure'


# リマインド
def remind(username, password, count):
    res = resemblance(username, password)
    if check_password(username, password):
        log_remind_success(username, count, res)
        return True
    else:
        if password == '':
            return False
        else:
            log_remind_failure(username, password, count,res)
            return False


# パスワード確認
def get_password(username):
    with open('./data/userlist.csv', 'r') as f:
        reader = csv.reader(f, lineterminator='\n')
        next(reader)
        for row in reader:
            if row[0] == username:
                return row[1]


# 表示pw文字列を作成
def hint(password, temppassword):
    results = init_hint(temppassword, password)
    str = []
    num = [[0 for i in range(4)] for j in range(len(results))]
    for i in range(len(results)):
        if results[i][1] == 'm':
            # 一致
            b = ''.join(results[i][0])
            str.append(b)
        elif results[i][1] == 'i':
            for a in range(len(results)):
                if results[a][0] == results[i][0] and results[a][1] == 'd':
                    if abs(i - a) == 2:
                        if i < a:
                            num[i + 1][3] += 1
                            num[a][2] += 1
                            num[i][3] += 1
                        else:
                            num[a + 1][3] += 1
                            num[a][2] += 1
                            num[a][3] += 1
                    else:
                        num[a][2] += 1
                else:
                    pass
            # 挿入
            str.append('☐')
        elif results[i][1] == 'd':
            # 削除
            str.append('×')
        else:
            # 置換
            str.append('△')

    # 隣接の順番違いに対応
    for b in range(len(results)):
        if num[b][3] > 0:
            str[b] = '△'
        elif num[b][2] > 0:
            del str[b]
        else:
            pass

    return str


# 一致、挿入、削除、置換をカウント
def count(results):
    i = 0
    d = 0
    r = 0
    m = 0
    for j in range(len(results)):
        if results[j] == '□':
            i += 1
        elif results[j] == '×':
            d += 1
        elif results[j] == '△':
            r += 1
        else:
            m += 1

    str = [m, i, d, r]
    return str


def hint_type(count):
    # 挿入＋削除＋置換も考える?
    if count[1] > 0 and count[3] > 0:
        # 挿入と置換
        type = 4
    elif count[2] > 0 and count[3] > 0:
        # 削除と置換
        type = 5
    elif count[1] > 0:
        # 挿入
        type = 1
    elif count[2] > 0:
        # 削除
        type = 2
    else:
        # 置換
        type = 3

    return type


def init_hint(password, temppassword):
    table = initialize_table(temppassword, password)
    calculated_table = calculate_cost(table, temppassword, password)
    results = judge_result(calculated_table, temppassword, password)
    return results


def initialize_table(word1: str, word2: str) -> List[List[Tuple[int, int, int]]]:
    # (スコア, 遷移前の座標x(row), 遷移前の座標y(column))
    table = [[(0, 0, 0)] * (len(word1) + 1) for i in range(len(word2) + 1)]

    for column in range(1, len(table[0])):
        table[0][column] = table[0][column - 1][0] + 7, 0, column - 1
    for row in range(1, len(table)):
        table[row][0] = table[row - 1][0][0] + 7, row - 1, 0
    return table


def calculate_cost(table: List[List[Tuple[int, int, int]]], word1: str, word2: str) -> List[List[Tuple[int, int, int]]]:
    for row in range(1, len(table)):
        for column in range(1, len(table[0])):
            if word1[column - 1] == word2[row - 1]:
                table[row][column] = table[row - 1][column - 1][0], row - 1, column - 1
            else:
                up_left = (table[row - 1][column - 1][0] + 10, row - 1, column - 1)
                left = (table[row][column - 1][0] + 7, row, column - 1)
                up = (table[row - 1][column][0] + 7, row - 1, column)
                table[row][column] = sorted([up_left, left, up], key=lambda x: x[0])[0]
    return table


def judge_result(table: List[List[Tuple[int, int, int]]], word1: str, word2: str) -> List[Tuple[str, str]]:
    results = []
    follow = (len(word2), len(word1))
    while follow != (0, 0):
        point = table[follow[0]][follow[1]]
        route = (point[1], point[2])

        if follow[0] == route[0]:
            results.append(([word1[route[1]]], 'd'))
        elif follow[1] == route[1]:
            results.append(([word2[route[0]]], 'i'))
        elif table[route[0]][route[1]][0] == point[0]:
            results.append(([word1[route[1]]], 'm'))
        else:
            results.append(([word1[route[1]], word2[route[0]]], 'r'))
        follow = route
    results.reverse()
    return results



if __name__ == '__main__':
    print(hint("Ck2e/eX7n5.&K","Ck2e/X7n5&.K"))