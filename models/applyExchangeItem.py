import sqlite3
from db import db 
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class ApplyExchangeItemModel(db.Model):
    __tablename__= "exchange_apply"
    id = db.Column(db.Integer,primary_key=True)
    itemId = db.Column(db.String(200),db.ForeignKey('exchange_items.itemId'))
    exchangeWay = db.Column(ARRAY(db.String))
    ownMember = db.Column(ARRAY(db.String))
    targetMember = db.Column(ARRAY(db.String))
    applier = db.Column(db.String(200),db.ForeignKey('users.userName'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    def __init__(self,itemId,exchangeWay,ownMember,targetMember,applier):
        self.itemId = itemId 
        self.exchangeWay = exchangeWay
        self.ownMember = ownMember     
        self.targetMember = targetMember
        self.applier = applier
    def json(self):
        return {
                'itemId':self.itemId, 
                'exchangeWay':self.exchangeWay,
                'ownMember':self.ownMember,
                'targetMember':self.targetMember,
                'applier':self.applier,
                } 
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
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_itemId_userName(cls,itemId,userName):
        return cls.query.filter_by(itemId=itemId,applier=userName).first()