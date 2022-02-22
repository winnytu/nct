from db import db 
import json
from datetime import datetime, timedelta,date
import time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import asc,desc

class EventModel(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    event_id = db.Column(db.String,unique=True)
    title = db.Column(db.String)
    sub_title = db.Column(db.String)
    url = db.Column(db.String)
    url_type = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    remark = db.Column(db.String)
    img = db.Column(db.String)
    show_status = db.Column(db.Integer,default = 0)
    content = db.Column(db.String)
    def __init__(self,event_id,title,sub_title,start_date,end_date,url,url_type,img,remark,content):
        self.event_id = event_id
        self.title = title
        self.sub_title = sub_title  
        self.start_date = start_date
        self.end_date = end_date
        self.url = url 
        self.url_type = url_type
        self.img = img
        self.remark = remark
        self.content = content
    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
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
    def find_by_id(cls,id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def find_by_event_id(cls,event_id):
        return cls.query.filter_by(event_id=event_id).first()
    @classmethod
    def find_by_start(cls):
        today = datetime.now()
        return cls.query.filter(cls.start_date<today).filter(cls.end_date>today).filter(cls.show_status != "0").order_by('start_date').all()
    
    @classmethod
    def find_by_end(cls):
        today = datetime.now()
        return cls.query.filter(cls.end_date<today).filter(cls.show_status != "0").order_by('start_date').all()