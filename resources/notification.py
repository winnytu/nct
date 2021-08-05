from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.notification import NotificationModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity
)
import json
class GetNotificationList(Resource):
    def post(self):
        data = request.get_json()
        notificationList = NotificationModel.find_by_user(data['userName'])
        return {
            'status':'success',
            'body':[item.to_dict() for item in notificationList ]
        }, 200
class GetNotificationCount(Resource):
    def post(self):
        data = request.get_json()
        notificationCount = NotificationModel.find_unread_num(data['userName'])
        return {
            'status':'success',
            'count':notificationCount
        }, 200
class ReadNotification(Resource):
    def post(self):
        data = request.get_json()
        notification = NotificationModel.find_by_id(data['id'])
        notification.status = 'read'
        notification.save_to_db()
        return {
            'status':'success',
        }, 200