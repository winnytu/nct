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

@app.route('/exchange/getItem', methods=['POST'])
def get_par02():
        conn = pymysql.connect(**db_settings)
        cursor = conn.cursor(cursor = pymysql.cursors.DictCursor)
        # 建立Cursor物件
        # 新增資料SQL語法
        command = "SELECT * FROM `exchangeitem`"
        cursor.execute(command)
        res = cursor.fetchall()
        return json.dumps(res)

@app.route('/exchange/addItem', methods=['POST'])
def get_par01():
        loginAccount = request.json['LoginAccount']
        groupName= request.json['groupName']
        category= request.json['category']
        album = request.json['album']
        desc = request.json['desc']
        exchangeWay = ",".join(request.json['exchangeWay']) 
        note = ",".join(request.json['note'])
        ownMember = ",".join(item.ownMember) 
        targetMember =",".join(item.targetMember)
        
 #建立Connection物件
        conn = pymysql.connect(**db_settings)
    # 建立Cursor物件
        with conn.cursor() as cursor:
        # 新增資料SQL語法
                addUserRecord = "INSERT INTO `exchangeUserTable` (`LoginAccount`,`groupName`,`category`,`album`,`desc`,`exchangeWay`,`note`,`ownMember`,`targetMember`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                records = (LoginName,groupName,category,album,desc,img,exchangeWay,note,ownMember,targetMember)
                cursor.execute(addUserRecord, records)
        conn.commit()
        return request.json

@app.route('/exchange/applyExchange', methods=['POST'])
def get_par02():
        loginAccount = request.json['LoginAccount']
        exchangeItemId = request.json['exchangeItemId']
        targetMember = request.json['targetMember']
        ownMember = request.json['ownMember']
        ExchangeWay = ",".join(request.json['ExchangeWay'])
        msg = request.json['msg']
        conn = pymysql.connect(**db_settings)
        cursor = conn.cursor(cursor = pymysql.cursors.DictCursor)
        # 建立Cursor物件
        # 新增資料SQL語法
        command = "SELECT * FROM `exchangeitem`"
        cursor.execute(command)c
        res = cursor.fetchall()
        return json.dumps(res)
if __name__ == '__main__':
        app.run(debug=True, port=5500)

#@app.route('/')                        代表是GET方法
#@app.route('/', methods=['GET'])       代表是GET方法
#@app.route('/', methods=['POST'])      代表是POST方法