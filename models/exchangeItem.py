import sqlite3
from db import db 
from datetime import datetime
from sqlalchemy import types
from sqlalchemy.dialects.postgresql import ARRAY

class ExchangeItemModel(db.Model):
    __tablename__= "exchange_items"
    id = db.Column(db.Integer,primary_key=True)
    itemId = db.Column(db.String(200),unique=True)
    groupName = db.Column(db.String(200))
    album = db.Column(db.String(200))
    category = db.Column(db.String(80))
    desc = db.Column(db.Text)
    exchangeWay = db.Column(ARRAY(db.String))
    note = db.Column(ARRAY(db.String))
    img = db.Column(db.LargeBinary)
    ownMember = db.Column(ARRAY(db.String))
    targetMember = db.Column(ARRAY(db.String))
    creator = db.Column(db.String(200),db.ForeignKey('users.userName'))
    relatedMessages= db.relationship('MessageModel',lazy='dynamic')
    relatedApplyItems= db.relationship('ApplyExchangeItemModel',lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    def __init__(self,itemId,groupName,album,category,desc,exchangeWay,note,img,ownMember,targetMember,creator):
        self.itemId = itemId 
        self.groupName = groupName
        self.album = album      
        self.category = category
        self.desc = desc
        self.exchangeWay = exchangeWay 
        self.note = note
        self.img = img
        self.ownMember = ownMember
        self.targetMember = targetMember
        self.creator = creator
    def json(self):
        return {
                'itemId':self.itemId, 
                'groupName':self.groupName,
                'album':self.album,
                'category':self.category,
                'desc':self.desc,
                'exchangeWay':self.exchangeWay,
                'note':self.note,
                'img':self.img,
                'ownMember':self.ownMember,
                'targetMember':self.targetMember,
                'creator':self.creator,
                } 
    def to_dict(self): 
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = str(datetime.date(getattr(self, key)))
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
    def find_by_itemId(cls,itemId):
        return cls.query.filter_by(itemId=itemId).first()
    @classmethod
    def find_by_creator(cls,creator):
        return cls.query.filter_by(creator=creator).all()
    @classmethod
    def find_related_messages(cls,itemId):
        return [item.to_dict() for item in cls.query.filter_by(itemId=itemId).first().relatedMessages]
    @classmethod
    def find_apply_messages(cls,itemId,applier,creator):
        itemList = cls.query.filter_by(itemId=itemId).first().relatedMessages
        newItemList = []
        for item in itemList:
            newItem = item.to_dict()
            if (newItem['fromUser'] == applier and newItem['toUser'] == creator) or (newItem['fromUser']== creator and newItem['toUser'] == applier):
                newItemList.append(newItem) 
            print(newItemList)
        return newItemList
    @classmethod
    def find_related_apply_items(cls,itemId):
        return [item.to_dict() for item in cls.query.filter_by(itemId=itemId).first().relatedApplyItems]
