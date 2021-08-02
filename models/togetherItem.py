import sqlite3
from db import db 
from datetime import datetime
from sqlalchemy import types
from sqlalchemy.dialects.postgresql import ARRAY

class TogetherItemModel(db.Model):
    __tablename__= "together_items"
    id = db.Column(db.Integer,primary_key=True)
    itemId = db.Column(db.String(200),unique=True)
    itemTitle = db.Column(db.String(200))
    groupName = db.Column(db.String(200))
    category = db.Column(db.String(80))
    desc = db.Column(db.Text)
    rule = db.Column(db.String(80))
    img = db.Column(db.LargeBinary)
    itemListA = db.Column(ARRAY(db.String))
    itemListB = db.Column(ARRAY(db.String))
    creator = db.Column(db.String(200),db.ForeignKey('users.userName'))
    expired_time = db.Column(db.DateTime)
    relatedMessages= db.relationship('TogetherMessageModel',lazy='dynamic')
    relatedApplyItems= db.relationship('ApplyTogetherItemModel',lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    def __init__(self,itemId,itemTitle,groupName,category,desc,img,rule,itemListA,itemListB,creator,expired_time):
        self.itemId = itemId 
        self.itemTitle= itemTitle
        self.groupName = groupName  
        self.category = category
        self.desc = desc
        self.img = img
        self.itemListA = itemListA
        self.itemListB = itemListB
        self.rule = rule
        self.creator = creator
        self.expired_time = expired_time
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
    def update_to_db(self):
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
    # @classmethod
    # def update_itemList(cls,itemId,newItemList):
    #     updateItemList = []
    #     item = cls.query.filter_by(itemId=itemId).first()
    #     for i in item.itemList:
    #         for j in newItemList:
    #             if (i[0] == j[0]):
    #                 i[1] = str(int(i[1])-int(j[1])) 
    #                 updateItemList.append(i)
    #     print(updateItemList)
    #     item.itemList = updateItemList
    #     item.update_to_db()
    #     print(cls.find_by_itemId(itemId).to_dict())
        