from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.notification import NotificationModel,NotificationUserModel
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity
)
import json
from imageSave import ImageSave
class CreateNotification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title',
        type = str,
        required = True,
        help = "請填寫標題"
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫類型"
    )
    parser.add_argument('content',
        type = str,
        required = True,
        help = "請填寫內容"
    )
    parser.add_argument('img',
        type = str,
        required = True,
        help = "請填寫圖片"
    )
    parser.add_argument('send_time',
        type = str,
        required = True,
        help = "請填寫發送時間"
    )
    parser.add_argument('send_type',
        type = str,
        required = True,
        help = "請填寫發送類型"
    )
    parser.add_argument('send_list',
        type = str,
        action = 'append',
        help = "請填寫發送類型"
    )
    def post(self):
        data = CreateNotification.parser.parse_args()
        notification = NotificationModel(data['title'],data['type'],data['content'],data['send_time'],data['send_type'])
        notification.send_list = data['send_list']
        notification.save_to_db()
        if data['img']:
            img = ImageSave(notification.id,data['img'],'notification').ImageSave()
            notification.img = img
            notification.save_to_db()
        
        if data['send_type'] == 'all':
            for user in UserModel.find_all():
                sender = NotificationUserModel(notification.id,user.user_id,data['send_time'])
                sender.save_to_db()
        else:
            # print(data)
            for user in data['send_list']:
                is_user = UserModel.find_by_user_id(user)
                if is_user is None:
                    notification.delete_from_db()
                    return {'errCode':'81111','errMsg':f'會員編號：{user}不存在'}
                sender = NotificationUserModel(notification.id,user,data['send_time'])
                sender.save_to_db()
        return {
            'status':'success',
            'body':'創建成功'
        }, 200
        
class EditNotification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
        type = str,
        required = True,
        help = "請填寫id"
    )
    parser.add_argument('title',
        type = str,
        required = True,
        help = "請填寫標題"
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫類型"
    )
    parser.add_argument('content',
        type = str,
        required = True,
        help = "請填寫內容"
    )
    parser.add_argument('img',
        type = str,
        required = True,
        help = "請填寫圖片"
    )
    parser.add_argument('send_time',
        type = str,
        required = True,
        help = "請填寫發送時間"
    )
    parser.add_argument('send_type',
        type = str,
        required = True,
        help = "請填寫發送類型"
    )
    parser.add_argument('send_list',
        type = str,
        action = 'append',
        help = "請填寫發送類型"
    )
    def post(self):
        data = EditNotification.parser.parse_args()
        notification = NotificationModel.find_by_id(data['id'])
        print(notification)
        notification.title = data['title']
        notification.type = data['type']
        notification.content = data['content']
        notification.send_time = data['send_time']
        notification.send_type = data['send_type']
        notification.send_list = data['send_list']
        if data['img']:
            img = ImageSave(notification.id,data['img'],'notification').ImageSave()
            notification.img = img
        notification.save_to_db()
        
        for item in NotificationUserModel.find_by_notification_id(notification.id):
            item.delete_from_db()
        
        if data['send_type'] == 'all':
            for user in UserModel.find_all():
                sender = NotificationUserModel(notification.id,user.user_id,data['send_time'])
                sender.save_to_db()
        else:
            # print(data)
            for user in data['send_list']:
                is_user = UserModel.find_by_user_id(user)
                if is_user is None:
                    notification.delete_from_db()
                    return {'errCode':'81111','errMsg':f'會員編號：{user}不存在'}
                sender = NotificationUserModel(notification.id,user,data['send_time'])
                sender.save_to_db()
        return {
            'status':'success',
            'body':'創建成功'
        }, 200
class GetAllNotification(Resource):
    def post(self):
        notificationList = NotificationModel.find_all()
        return {
            'status':'success',
            'body':[item.to_dict() for item in notificationList ]
        }

class GetNotificationList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id',
        type = str,
        required = True,
        help = "請填寫userid"
    )
    def post(self):
        data = GetNotificationList.parser.parse_args()
        notificationList = NotificationUserModel.find_by_user_sent(data['user_id'])
        list = []
        for item in notificationList:
            if item.status != 3:
                notification_item = {}
                notification_item = NotificationModel.find_by_id(item.notification_id).to_dict()
                notification_item['status'] = item.status
                notification_item['notification_id'] = item.id
                list.append(notification_item)
        return {
            'status':'success',
            'body':list,
            'count':NotificationUserModel.find_unread_num(data['user_id'])
        }, 200

class GetNotificationCount(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id',
        type = str,
        required = True,
        help = "請填寫userid"
    )
    def post(self):
        data = GetNotificationCount.parser.parse_args()
        notificationCount = NotificationUserModel.find_unread_num(data['user_id'])
        return {
            'status':'success',
            'count':notificationCount
        }, 200
        
# 已讀通知
class ReadNotification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id',
        type = str,
        required = True,
        help = "請填寫user_id"
    )
    def post(self):
        data = ReadNotification.parser.parse_args()
        notification = NotificationUserModel.find_by_user(data['user_id'])
        for item in notification:
            if item.status == 0:
                item.status = 1
                item.save_to_db()
        return {
            'status':'success',
        }, 200

# 刪除通知
class HideNotification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('notification_id',
        type = str,
        required = True,
        help = "請填寫notification_id"
    )
    def post(self):
        data = HideNotification.parser.parse_args()
        notification = NotificationUserModel.find_by_id(data['notification_id'])
        notification.status = 3
        notification.save_to_db()
        return {
            'status':'success',
        }, 200


class HideAllNotification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('notification_id',
        type = str,
        required = True,
        help = "請填寫notification_id"
    )
    def post(self):
        data = HideAllNotification.parser.parse_args()
        notification_item = NotificationModel.find_by_id(data['notification_id'])
        notification_item.status = 2
        notification_item.save_to_db()
        notification = NotificationUserModel.find_by_notification_id(data['notification_id'])
        for item in notification:
            item.status = 3
            item.save_to_db()
        return {
            'status':'success',
        }, 200