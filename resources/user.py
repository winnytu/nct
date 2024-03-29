from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.user import UserModel
from models.notification import NotificationModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import json
class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
        type = str,
        required = True,
        help = "請填寫email"
    )
    parser.add_argument('password',
        type = str,
        required = True,
        help = "請填寫密碼"
    )
    parser.add_argument('userName',
        type = str,
        required = True,
        help = "請填寫暱稱"
    )

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_email(data['email']):
            return {'errCode':'80001','errMsg':'該信箱已註冊過'}
        elif UserModel.find_by_userName(data['userName']):
            return {'errCode':'80002','errMsg':'該暱稱已被使用'}
        user = UserModel(**data)
        user.save_to_db()
        userInfo = UserModel.find_by_email(data['email']).to_dict()
        newNotification = NotificationModel('unread','系統','註冊成功','歡迎加入米粉湯',data['userName'])
        newNotification.save_to_db()
        return {'status':'success','body':userInfo}

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
        type = str,
        required = True,
        help = "請填寫email"
    )
    parser.add_argument('password',
        type = str,
        required = True,
        help = "請填寫密碼"
    )
    def post(self):
        data = UserLogin.parser.parse_args()
        user = UserModel.find_by_email(data['email'])
        if user and safe_str_cmp(user.password,data['password']):
            access_token = create_access_token(identity=data['email'],fresh=True)
            refresh_token = create_refresh_token(identity=data['email'])
            userInfo = user.to_dict()
            print(userInfo)
            userInfo['access_token'] = access_token
            userInfo['refresh_token'] = refresh_token
            return {'status':'success','body':userInfo}
        else:
            return {'errCode':'80003','errMsg':'登入失敗'}

class UserItem(Resource):
    def post(self):
        data = request.get_json()
        
        if data['type'] == 'exchange':
            return {
                'status':'success',
                'body':{
                    'myExchangeList':UserModel.allExchangeItem(data['userName']),
                    'myApplyExchangeList':UserModel.allApplyExchangeItems(data['userName'])
                }           
            }, 200
        elif data['type'] == 'together':
            return {
                 'status':'success',
                'body':{
                    'myTogetherList':UserModel.allTogetherItem(data['userName']),
                    'myApplyTogetherList':UserModel.allApplyTogetherItems(data['userName'])
                }         
            },200
        elif data['type'] == '':
            return {
                'status':'success',
                'body':{
                    'myExchangeList':UserModel.allExchangeItem(data['userName']),
                    'myApplyExchangeList':UserModel.allApplyExchangeItems(data['userName']),
                    'myTogetherList':UserModel.allTogetherItem(data['userName']),
                    'myApplyTogetherList':UserModel.allApplyTogetherItems(data['userName'])
                }         
            },200

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user=get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=false)
        return {'access_token':new_token}

