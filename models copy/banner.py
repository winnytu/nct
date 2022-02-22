from db import db 
import json
from datetime import datetime, timedelta,date
import time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import asc,desc
from itertools import groupby
from operator import attrgetter


class BannerModel(db.Model):
    __tablename__ = 'banner'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    order = db.Column(db.Integer)
    position = db.Column(db.String)
    title = db.Column(db.VARCHAR(80))
    url = db.Column(db.String)
    url_type = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    img = db.Column(db.String)
    text = db.Column(db.String)
    device = db.Column(db.String)
    video_url = db.Column(db.String)
    show_status =  db.Column(db.Integer,default=0)
    def __init__(self,position,order,title):
        self.order = order
        self.position = position
        self.title = title
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
    def find_by_position(cls,position,device):
        group = {}
        for position_ in position:
            group[position_] = [item.to_dict() for item in cls.query.filter_by(position=position_).filter_by(device=device).filter_by(show_status=1).order_by('order').all()]
        return group

    @classmethod
    def find_by_device(cls,device):
        lists = cls.query.filter_by(device=device).order_by('position',asc('order')).all()
        groups = {}
        for k, g in groupby(lists, attrgetter('position')):
            groups[k]=[item.to_dict() for item in list(g)]  
        return groups
    @classmethod
    def find_by_id(cls,id):
        return cls.query.filter_by(id=id).first()
    @classmethod
    def find_by_show(cls,position):
        today = date.today()
        return cls.query.filter_by(position=position).filter(cls.start_date<today).filter(cls.end_date>today).filter(cls.show_status != "0").order_by('order').all()