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
                'itemId ':self.itemId, 
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
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()