# サーバー起動時の初期操作を記述する(面倒なので)
import os

DATA_DIR_PATH = './data'

if os.path.exists(DATA_DIR_PATH) == False:
    os.mkdir(DATA_DIR_PATH)