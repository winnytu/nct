import os

from flask import Flask,make_response
from flask_restful import Api
# resource creating some data
from flask_jwt_extended import JWTManager
from resources.user import UserRegister,UserLogin,UserItem
from resources.exchangeItem import CreateItem, ModifyItem,ItemList,MessageList
from resources.applyExchangeItem import ApplyExchangeItem
from resources.message import SendMessage
from db import db

from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
uri = os.environ.get("DATABASE_URL",'postgresql://postgres:Aa082315@localhost/nct')   # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
db.init_app(app)
api = Api(app)

# create table
@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

api.add_resource(UserLogin,'/user/login')
api.add_resource(UserRegister,'/user/register')
api.add_resource(CreateItem,'/exchange/createItem')
api.add_resource(ModifyItem,'/exchange/modifyItem')
api.add_resource(ItemList,'/exchange/itemList')
api.add_resource(MessageList,'/exchange/messageList')
api.add_resource(ApplyExchangeItem,'/exchange/applyItem')
api.add_resource(UserItem,'/user/myItemList')
api.add_resource(SendMessage,'/message/send')

# 只要在run這個檔案的時候才會執行 沒加的話則是import的時候就會執行
if __name__ == "__main__":
    app.run(port=5000)
