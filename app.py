import os

from flask import Flask,make_response
from flask_restful import Api
# resource creating some data
from flask_jwt_extended import JWTManager
from resources.user import UserRegister,UserLogin,UserItem,TokenRefresh
from resources.exchangeItem import CreateExchangeItem, ModifyExchangeItem,ExchangeItemList,ExchangeMessageList,GetExchangeApplyList
from resources.applyExchangeItem import ApplyExchangeItem,CheckApplyStatus
from resources.togetherItem import CreateTogetherItem,TogetherItemList,TogetherMessageList,GetTogetherApplyList
from resources.applyTogetherItem import ApplyTogetherItem
from resources.message import SendExchangeMessage,SendTogetherMessage
from resources.notification import GetNotificationList,ReadNotification,GetNotificationCount
from db import db

from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
uri = os.environ.get("DATABASE_URL",'postgresql://postgres:Aa082315@localhost/nct')   # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)
db.init_app(app)
api = Api(app)

# create table
@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_payload, jwt_headers):
    return {
        'message': '憑證過期',
        'errCode': '80080'
    }, 401

api.add_resource(UserLogin,'/user/login')
api.add_resource(UserRegister,'/user/register')
api.add_resource(TokenRefresh,'/user/refresh')
api.add_resource(CreateExchangeItem,'/exchange/createItem')

api.add_resource(ModifyExchangeItem,'/exchange/modifyItem')
api.add_resource(ExchangeItemList,'/exchange/itemList')
api.add_resource(ExchangeMessageList,'/exchange/messageList')
api.add_resource(ApplyExchangeItem,'/exchange/applyItem')
api.add_resource(ApplyTogetherItem,'/together/applyItem')
api.add_resource(GetExchangeApplyList,'/exchange/getApplyList')
api.add_resource(CheckApplyStatus,'/exchange/checkApplyStatus')
api.add_resource(UserItem,'/user/myItemList')
api.add_resource(SendExchangeMessage,'/exchange/sendMessage')
api.add_resource(SendTogetherMessage,'/together/sendMessage')

api.add_resource(CreateTogetherItem,'/together/createItem')
api.add_resource(TogetherItemList,'/together/itemList')
api.add_resource(TogetherMessageList,'/together/messageList')
api.add_resource(GetTogetherApplyList,'/together/getApplyList')

api.add_resource(GetNotificationList,'/notification/list')
api.add_resource(GetNotificationCount,'/notification/count')
api.add_resource(ReadNotification,'/notification/read')
# 只要在run這個檔案的時候才會執行 沒加的話則是import的時候就會執行
if __name__ == "__main__":
    app.run(port=5000)
