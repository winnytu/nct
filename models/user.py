import sqlite3
from db import db 
from itemIdGenerator import DateEncoder
import json
from datetime import datetime

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.VARCHAR(80),unique=True)
    password = db.Column(db.VARCHAR(80))
    userName = db.Column(db.VARCHAR(80),unique=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    exchangeItems = db.relationship('ExchangeItemModel',lazy='dynamic')
    applyItems = db.relationship('ApplyExchangeItemModel',lazy='dynamic')

    def __init__(self,email,password,userName):
        self.email = email
        self.password = password
        self.userName = userName

    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = str(getattr(self, key))
            elif key == 'password':
                continue
            else:
                result[key] = getattr(self, key)
        return result

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_by_email(cls,email):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def find_by_userName(cls,userName):
        return cls.query.filter_by(userName=userName).first()
    @classmethod
    def allExchangeItem(cls,userName):
        return [item.json() for item in cls.query.filter_by(userName=userName).first().exchangeItems]
    @classmethod
    def allApplyItems(cls,userName):
        return [item.json() for item in cls.query.filter_by(userName=userName).first().applyItems]
    @classmethod
    def allMessagesSended(cls,userName):
        return [item.json() for item in cls.query.filter_by(userName=userName).first().msgSendedList]
    @classmethod
    def allMessagesReceived(cls,userName):
        return [item.json() for item in cls.query.filter_by(userName=userName).first().msgReceivedList]