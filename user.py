from flask import Flask,request,make_response,jsonify,Response
from flask_cors import CORS
import pymysql
import json

db_settings = {
        "host":"127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "22013788",
        "db":"exchange",
        "charset":"utf8"
}

# try:
#     # 建立Connection物件
#     conn = pymysql.connect(**db_settings)

#     # 建立Cursor物件
#     with conn.cursor() as cursor:
#         # 新增資料SQL語法
#         command = "INSERT INTO charts(id, name, artist)VALUES(%s, %s, %s)"


# except Exception as ex:
#     print(ex)

app = Flask(__name__)
CORS(app)

@app.route('/user/register', methods=['POST'])
def userRegister():
        return json.dumps(res)

@app.route('/user/login', methods=['POST'])
def userRegister():
        return json.dumps(res)

@app.route('/user/logout', methods=['POST'])
def userRegister():
        return json.dumps(res)


if __name__ == '__main__':
        app.run(debug=True, port=5500)

#@app.route('/')                        代表是GET方法
#@app.route('/', methods=['GET'])       代表是GET方法
#@app.route('/', methods=['POST'])      代表是POST方法