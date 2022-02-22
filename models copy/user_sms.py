from db import db 
from datetime import datetime
from sqlalchemy import and_

class UserSMSModel(db.Model):
    __tablename__= "user_sms"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    phone_number = db.Column(db.VARCHAR(20))
    sms_code = db.Column(db.VARCHAR(6))
    create_time = db.Column(db.DateTime, default=datetime.now)
    is_valid = db.Column(db.Boolean, default=True)
    sms_type = db.Column(db.SmallInteger, default=1)

    def __init__(self, phone_number, sms_code, sms_type):
        self.phone_number = phone_number
        self.sms_code = sms_code
        self.sms_type = sms_type

    @classmethod
    def find_by_valid(cls, phone_number, sms_code, sms_type):
        return cls.query.filter(and_(cls.phone_number==phone_number, cls.sms_code==sms_code, cls.sms_type==sms_type, cls.is_valid==True)).order_by(cls.id.desc()).first()
    
    '''
    @classmethod
    def find_by_phone(cls, phone_number, sms_code):
        return cls.query.filter(cls.phone_number==phone_number).order_by(cls.id.desc()).first()
    '''

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()