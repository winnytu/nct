from flask import Flask,request,make_response,jsonify,Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/exchange/getItem', methods=['POST'])
def get_par01():
 group = request.json['group']
 category= request.json['category']
 ownMember = request.json['ownMember']
 targetMember = request.json['targetMember']
 ways = request.json['ways']
 return request.json

@app.route('/exchange/addItem', methods=['POST'])
def get_par01():
 group = request.json['group']
 category= request.json['category']
 ownMember = request.json['ownMember']
 targetMember = request.json['targetMember']
 ways = request.json['ways']
 return request.json

if __name__ == '__main__':
        app.run(debug=True, port=5500)

#@app.route('/')                        代表是GET方法
#@app.route('/', methods=['GET'])       代表是GET方法
#@app.route('/', methods=['POST'])      代表是POST方法