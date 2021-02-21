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
        groupName= request.json['groupName']
        category= request.json['category']
        ownMember = request.json['ownMember']
        # 一定要轉成字串
        targetMember =",".join(request.json['targetMember']) 
        exchangeWay = ",".join(request.json['exchangeWay']) 
        
 #建立Connection物件
        conn = pymysql.connect(**db_settings)
    # 建立Cursor物件
        with conn.cursor() as cursor:
        # 新增資料SQL語法
                add = "INSERT INTO `exchangeitem` (`name`,`category`,`ownMember`,`targetMember`,`exchangeWay`) VALUES (%s,%s,%s,%s,%s)"
                records = (groupName,  category,ownMember,targetMember,exchangeWay)
                cursor.execute(add, records)
        conn.commit()
        return request.json
if __name__ == '__main__':
        app.run(debug=True, port=5500)

#@app.route('/')                        代表是GET方法
#@app.route('/', methods=['GET'])       代表是GET方法
#@app.route('/', methods=['POST'])      代表是POST方法