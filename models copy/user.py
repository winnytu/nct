import sqlite3
from typing import DefaultDict
from db import db 
import json
from datetime import datetime,date,timedelta

class UserModel(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id = db.Column(db.String,unique=True)
    phone = db.Column(db.VARCHAR(80),unique=True)
    password = db.Column(db.VARCHAR)
    user_name = db.Column(db.VARCHAR)
    avatar = db.Column(db.VARCHAR,default="https://storage.googleapis.com/sport168-image/default/avatar.jpg")
    info = db.Column(db.VARCHAR(100))
    dist = db.Column(db.VARCHAR(100))
    gender = db.Column(db.VARCHAR(100))
    birth = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime, default=datetime.now)
    last_login_time = db.Column(db.DateTime, default=datetime.now)
    created_ip = db.Column(db.VARCHAR)
    last_login_ip = db.Column(db.VARCHAR)
    account_status = db.Column(db.Integer,default=1)
    chat_status = db.Column(db.Integer,default=1)
    publish_status = db.Column(db.Integer,default=1)
    # notification_list = db.relationship('NotificationModel')
    like_list = db.relationship('LikeModel')
    comment_list = db.relationship('CommentModel',backref="commenter")
    notification_list = db.relationship('NotificationUserModel')
    def __init__(self,phone,ip):
        self.phone = phone
        self.created_ip = ip
    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'password' or key == 'id':
                continue
            else:
                result[key] = getattr(self, key)
        return result

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    @classmethod
    def find_all(cls):
        return cls.query.all()
    @classmethod
    def find_by_phone(cls,phone):
        return cls.query.filter_by(phone=phone).first()
    @classmethod
    def find_by_user_id(cls,user_id):
        return cls.query.filter_by(user_id=user_id).first()
    @classmethod
    def find_by_user_name(cls,user_name):
        return cls.query.filter_by(user_name=user_name).first()
    @classmethod
    def find_today_register(cls):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        today_count = cls.query.filter(cls.created_time>today).filter(cls.created_time<tomorrow).count()
        return today_count
