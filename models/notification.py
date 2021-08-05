import sqlite3
from db import db 
from datetime import datetime

class NotificationModel(db.Model):
    __tablename__= "notification"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80))
    type = db.Column(db.String(80))
    content = db.Column(db.Text)
    status = db.Column(db.String(80))
    toUser = db.Column(db.String(200),db.ForeignKey('users.userName'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    def __init__(self,status,type,title,content,toUser):
        self.title = title
        self.type = type
        self.status = status
        self.content = content
        self.toUser = toUser
    def to_dict(self): 
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = str(getattr(self, key))
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
    def find_by_user(cls,toUser):
        return cls.query.filter_by(toUser=toUser).all()
    @classmethod
    def find_unread_num(cls,toUser):
        return cls.query.filter_by(toUser=toUser).filter_by(status='unread').count()
    @classmethod
    def find_by_id(cls,id):
        return cls.query.filter_by(id=id).first()