import sqlite3
from db import db 
from datetime import datetime

class TogetherMessageModel(db.Model):
    __tablename__= "together_messages"
    id = db.Column(db.Integer,primary_key=True)
    postMessage = db.Column(db.Text)
    status = db.Column(db.String(80))
    fromUser = db.Column(db.String(200),db.ForeignKey('users.userName'))
    toUser = db.Column(db.String(200),db.ForeignKey('users.userName'))
    relatedItem = db.Column(db.String(200),db.ForeignKey('together_items.itemId'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    def __init__(self,status,postMessage,fromUser,toUser,relatedItem):
        self.status = status
        self.postMessage = postMessage
        self.toUser = toUser
        self.fromUser = fromUser      
        self.relatedItem = relatedItem
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