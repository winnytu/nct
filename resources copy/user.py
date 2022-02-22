from flask import request,after_this_request
from flask_restful import Resource,reqparse,request,fields,marshal
from models.user import UserModel
from models.user_sms import UserSMSModel
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
from datetime import datetime
import time
from base import Base

from idGenerator import IdWorker
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client  # import 套件
from imageSave import ImageSave
account_sid = "AC85901905795f9f97d45483c4e4e081e5" # 請填寫剛剛紀錄的 ACCOUNT SID
auth_token = "5093809e758b32c9202316c9ed87cc53" # 請填寫剛剛紀錄的 AUTH TOKEN
service_sid = "VAca8ee7d6a422d4090a0aaaa6f503df4d"
# 建立 client instance
client = Client(account_sid, auth_token)

class UserRegister(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type = str, required = True, help = "please input mobile phone number.")
    parser.add_argument('code', type = str, required = True, help = "please input sms code.")
    parser.add_argument('password', type = str, required = True, help = "please input password.")

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_phone(data['phone']):
            return self.cook_return(604)

        user = UserModel(data['phone'],request.remote_addr)
        user.save_to_db()
        user.user_id = IdWorker(1,1,user.id).get_id()
        user.user_name = self.lang['TITLE'] + str(IdWorker(1,1,user.id).get_id())[14:]
        user.last_login_ip = request.remote_addr
        user.password = self.gen_password(data['password'])
        user.save_to_db()
        
        userInfo = user.to_dict()
        access_token = create_access_token(identity=user.user_id,fresh=True)
        refresh_token = create_refresh_token(identity=user.user_id)
        userInfo['access_token'] = access_token
        userInfo['refresh_token'] = refresh_token
        return self.cook_return(200, '', userInfo)

class SendVerification(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type = str, required = True, help = "please input mobile phone number.") 

    def post(self):
        data = SendVerification.parser.parse_args()
        if (sms_code := self.send_sms(data['phone'])):
            sms = UserSMSModel(data['phone'], sms_code, 1)
            sms.save_to_db()
            return self.cook_return(200, '', {})
        else:
            return self.cook_return(608)

class UserPhoneLogin(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type = str, required = True, help = "please input mobile phone number.")
    parser.add_argument('code', type = str, required = True, help = "please input sms code.")
    parser.add_argument('User-Agent', location='headers')
    def post(self):
        data = UserPhoneLogin.parser.parse_args()

        #check user_sms table record 
        if (sms := UserSMSModel.find_by_valid(data['phone'], data['code'], 1)):
            sms.phone_number = data['phone']
            sms.is_valid = False ##tag invalid
            sms.save_to_db()
        else: #add sentry of exception in future
            return self.cook_return(605)

        #member exist, add login record
        if (user := UserModel.find_by_phone(data['phone'])):
            
            #status is abnormal
            if user.account_status == 0:
                return self.cook_return(403)
            else:      
                #insert to user_login table next time
                user.last_login_time = datetime.now()
                user.last_login_ip = request.remote_addr

            #Authorization: Bearer token if token non-expired then update lifetime

        else: #not member, create a member info
            user = UserModel(data['phone'], request.remote_addr)
            user.save_to_db()
            user.user_id = IdWorker(1,1,user.id).get_id()
            user.user_name = self.lang['TITLE'] + str(IdWorker(1,1,user.id).get_id())[14:]
            user.last_login_ip= request.remote_addr

        user.save_to_db()    
        userInfo = user.to_dict() # return as dict

        #only happen at first time 
        userInfo['access_token'] = create_access_token(identity=user.user_id,fresh=True)
        userInfo['refresh_token'] = create_refresh_token(identity=user.user_id)
        return self.cook_return(200, '', userInfo)
        
class UserPasswordLogin(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type = str, required = True, help = "please input mobile phone number.")
    parser.add_argument('password', type = str, required = True, help = "please input password.")

    def post(self):
        data = UserPasswordLogin.parser.parse_args()
        if (user := UserModel.find_by_phone(data['phone'])):
            
            #status is abnormal
            if user.account_status == 0: 
                return self.cook_return(403)
            elif self.check_password(user.password, data['password']):
                #insert to user_login table in the future
                user.last_login_time = datetime.now()
                user.last_login_ip = request.remote_addr
                user.save_to_db()

                userInfo = user.to_dict()
                refresh_token = create_refresh_token(identity=user.user_id)
                access_token = create_access_token(identity=user.user_id,fresh=True)
                userInfo['access_token'] = access_token
                userInfo['refresh_token'] = refresh_token
                @after_this_request
                def set_is_bar_cookie(response):
                    response.set_cookie(refresh_token, 'no', max_age=64800,expires=time.time()+15*60 ,httponly=True)
                    return response
                return self.cook_return(200, '', userInfo)
            else:
                return self.cook_return(601) #password not match
        else:
            return self.cook_return(602) #phone number not found

class ResetPassword(Resource, Base):
    def post(self):
        data = request.get_json()
    
        if (user := UserModel.find_by_phone(data['phone'])):

            #only for admin, remove it in the future and pls carefully when u use it.
            if data.get('superUser'):
                user.password= data['password']
                user.save_to_db()
                return self.cook_return(200)

            #real api flow
            parser = reqparse.RequestParser()
            parser.add_argument('phone', type = str, required = True, help = "please input mobile phone number.")
            parser.add_argument('password', type = str, required = True, help = "please input password.")
            parser.add_argument('code', type = str, required = True, help = "please input sms code.")
            #check sms code is valid to use.
            if (sms := UserSMSModel.find_by_valid(data['phone'], data['code'], 1)):
                sms.phone_number = data['phone']
                sms.is_valid = False #tag invalid
                sms.save_to_db()
                
                #update password of record
                user.password= self.gen_password(data['password'])
                user.save_to_db()
                return self.cook_return(200)
            else:
                return self.cook_return(605) #invalid sms code
        else:
            return self.cook_return(607) #invalid phone number

class UserAvatar(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type = str, required = True, help = "please input user id.")
    parser.add_argument('avatar', type = str, required = True, help = "please input avatar.")

    @jwt_required()
    def post(self):
        data = UserAvatar.parser.parse_args()
        if (user := UserModel.find_by_user_id(data['user_id'])):
            img = ImageSave(data['user_id'],data['avatar'],'user').ImageSave()
            user.avatar = img
            user.save_to_db()
            return self.cook_return(200, '', user.to_dict())
        else:
            return self.cook_return(606) #user id not found

class UserUpdate(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('phone', type = int, required = True, help = "please input mobile phone number.",)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        user = UserModel.find_by_phone(data['phone'])
        if (user := UserModel.find_by_phone(data['phone'])):
            user.user_name = data.get('user_name')
            user.info = data.get('info')
            user.dist = data.get('dist')
            user.gender = data.get('gender')
            user.birth = data.get('birth')
            user.save_to_db()
            return self.cook_return(200, '', user.to_dict())
        else:
            return self.cook_return(607) #invalid phone number

class TokenRefresh(Resource, Base):
    @jwt_required(refresh=True)
    def post(self):
        current_user=get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)
        return self.cook_return(200, '', {'access_token' : new_token})

class GetUserInfo(Resource, Base):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user)
        return self.cook_return(200, '', user.to_dict())

class GetUserList(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('userId',
        type = int,
        required = False,
        help = "please input user id",
        default = 1
    )
    parser.add_argument('user_name',
        type = int,
        required = False,
        help = "please input user name",
        default = 1
    )
    parser.add_argument('page',
        type = int,
        required = False,
        help = "please input page number",
        default = 1
    )
    parser.add_argument('pageSize',
        type = int,
        required = False,
        help = "please input page size",
        default  = 10
    )
    def post(self):
        data = GetUserList.parser.parse_args()
        userList = []
        total = UserModel.query.limit(data['pageSize']).offset((data['page']*10)-10).count()
        for user in UserModel.query.limit(data['pageSize']).offset((data['page']*10)-10).all():
            user_info = user.to_dict()
            user_info['comment'] = len(user.comment_list)
            userList.append(user_info)
        return self.cook_return(200, '', {'userList' : userList, 'today_register' : UserModel.find_today_register(), 'total' : total})

class GetUserDetail(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('userId', type = str, required = True, help = "please input user id.", default = 1)
    def post(self):
        data = GetUserDetail.parser.parse_args()
        if (user := UserModel.find_by_user_id(data['userId'])):
            return self.cook_return(200, '', user.to_dict())
        return self.cook_return(200, '', '')

class ToggleUserStatus(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('userIdList', type = str, action = 'append', required = True, help = "please input user id.", default = 1)
    parser.add_argument('status', type = str, required = True, help = "please input user status.", default = 1)
    def post(self):
        data = ToggleUserStatus.parser.parse_args()
        for id in data['userIdList']:
            if (user := UserModel.find_by_user_id(id)):
                user.account_status = data['status']
                user.save_to_db()
        return self.cook_return(200, '', '')

class ToggleUserChatStatus(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('userIdList', type = str, action='append', required = True, help = "please input user id.", default = 1)
    parser.add_argument('status', type = str, required = True, help = "please input user status.", default = 1)
    def post(self):
        data = ToggleUserChatStatus.parser.parse_args()
        for id in data['userIdList']:
            if (user := UserModel.find_by_user_id(id)):
                user.chat_status = data['status']
                user.save_to_db()
        return self.cook_return(200, '', '')

class ToggleUserPublishStatus(Resource, Base):
    parser = reqparse.RequestParser()
    parser.add_argument('userIdList', type = str, action='append', required = True, help = "please input user id.", default = 1)
    parser.add_argument('status', type = str, required = True, help = "please input user status.", default = 1)
    def post(self):
        data = ToggleUserPublishStatus.parser.parse_args()
        for id in data['userIdList']:
            if (user := UserModel.find_by_user_id(id)):
                user.publish_status = data['status']
                user.save_to_db()
        return self.cook_return(200, '', '')