import sqlite3
from db import db 
from datetime import datetime

class MessageModel(db.Model):
    __tablename__= "messages"
    id = db.Column(db.Integer,primary_key=True)
    postMessage = db.Column(db.Text)
    status = db.Column(db.String(80))
    fromUser = db.Column(db.String(200),db.ForeignKey('users.userName'))
    toUser = db.Column(db.String(200),db.ForeignKey('users.userName'))
    relatedItem = db.Column(db.String(200),db.ForeignKey('exchange_items.itemId'))
    create_time = db.Column(db.DateTime, default=datetime.now)
    def __init__(self,status,postMessage,fromUser,toUser,relatedItem):
        self.status = status
        self.postMessage = postMessage
        self.fromUser = fromUser      
        self.toUser = toUser
        self.relatedItem = relatedItem
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()