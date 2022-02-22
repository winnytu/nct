import sqlite3
from db import db 
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import asc,desc
from datetime import datetime,timedelta

class NotificationModel(db.Model):
    __tablename__= "notification"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80))
    type = db.Column(db.String(80))
    img = db.Column(db.String)
    content = db.Column(db.Text)
    created_time = db.Column(db.DateTime, default=datetime.now)
    send_time = db.Column(db.DateTime)
    send_type = db.Column(db.String)
    send_list = db.Column(ARRAY(db.String))
    # 1 正常 2 回收
    status = db.Column(db.Integer, default=1)
    receive_list = db.relationship('NotificationUserModel')
    def __init__(self,title,type,content,send_time,send_type):
        self.title = title
        self.type = type
        self.content = content
        self.send_time = send_time
        self.send_type = send_type
    def to_dict(self): 
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            else:
                result[key] = getattr(self, key)
        return result  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.order_by(desc('created_time')).all()
    @classmethod
    def find_by_id(cls,id):
        return cls.query.filter_by(id=id).first()

class NotificationUserModel(db.Model):
    __tablename__= "notification_user"
    id = db.Column(db.Integer,primary_key=True)
    notification_id = db.Column(db.Integer,db.ForeignKey('notification.id'))
    # 0 未讀 1 已讀 3 刪除
    status = db.Column(db.Integer,default=0)
    to_user = db.Column(db.String,db.ForeignKey('member.user_id'))
    send_time = db.Column(db.DateTime)
    def __init__(self,notification_id,to_user,send_time):
        self.notification_id = notification_id
        self.to_user = to_user
        self.send_time = send_time
    def to_dict(self): 
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            else:
                result[key] = getattr(self, key)
        return result  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_user(cls,to_user):
        return cls.query.filter_by(to_user=to_user).order_by(desc('send_time')).all()
    @classmethod
    def find_by_user_sent(cls,to_user):
        now = datetime.utcnow() + timedelta(hours=8)
        return cls.query.filter_by(to_user=to_user).filter(cls.send_time<now).order_by(desc('send_time')).all()
    @classmethod
    def find_unread_num(cls,to_user):
        now = datetime.utcnow()+ timedelta(hours=8)
        return cls.query.filter_by(to_user=to_user).filter_by(status=0).filter(cls.send_time<now).count()
    @classmethod
    def find_by_id(cls,id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def find_by_notification_id(cls,notification_id):
        return cls.query.filter_by(notification_id=notification_id).all()