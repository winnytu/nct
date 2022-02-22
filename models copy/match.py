import sqlite3
from db import db 
import json
from datetime import datetime,date,timedelta
import time
from sqlalchemy import asc,desc


from models.category import SubCategoryModel,MainCategoryModel

class MatchModel(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer,primary_key=True)
    match_id =  db.Column(db.String,unique=True)
    category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category_sub.sub_category_id'))
    stage_name = db.Column(db.String)
    match_date = db.Column(db.String)
    match_time = db.Column(db.DateTime)
    match_status = db.Column(db.String)
    match_hour = db.Column(db.String)
    home_name = db.Column(db.String)
    home_logo = db.Column(db.String)
    home_score = db.Column(db.String)
    away_name = db.Column(db.String)
    away_logo = db.Column(db.String)
    away_score = db.Column(db.String)
    show_status =db.Column(db.String,default=1)
    def __init__(self,category_id,sub_category_id,match_date,match_time,match_status):
        self.category_id=  category_id
        self.sub_category_id = sub_category_id
        self.match_date = match_date
        self.match_time = match_time
        self.match_status = match_status
    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'password':
                continue
            else:
                result[key] = getattr(self, key)
        return result

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_by_match_id(cls,match_id):
        return cls.query.filter_by(match_id=match_id).first()
    @classmethod
    def find_by_match_today(cls,sub_category_id):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return cls.query.filter_by(sub_category_id=sub_category_id).filter(cls.match_time>today).filter(cls.match_time<tomorrow).count()

    @classmethod
    def find_by_category_id(cls,category_id):
        list = []
        for i in range(7):
            item = {}
            item['date'] = str(date.today()+timedelta(days = i))
            match_list = []
            for match in cls.query.filter_by(category_id=category_id).filter_by(match_date=item['date']).order_by(asc('match_time')).all():
                match_item = match.to_dict()
                match_item['category'] = SubCategoryModel.find_by_sub_category(match.sub_category_id).sub_category
                match_item['sport_id'] = MatchLiveModel.find_by_match_id(match.match_id).match_type_1
                match_list.append(match_item)
            if len(match_list)>0:
                item['matchList'] = match_list
                list.append(item)
        return list
    @classmethod
    def find_by_sub_category_id(cls,sub_category_id):
        list = []
        for i in range(7):
            item = {}
            item['date'] = str(date.today()+timedelta(days = i))
            match_list = []
            for match in cls.query.filter_by(sub_category_id=sub_category_id).filter_by(match_date=item['date']).order_by(asc('match_time')).all():
                match_item = match.to_dict()
                match_item['category'] = SubCategoryModel.find_by_sub_category(sub_category_id).sub_category
                match_item['sport_id'] = MatchLiveModel.find_by_match_id(match.match_id).match_type_1
                match_list.append(match_item)
            if len(match_list)>0:
                item['matchList'] = match_list
                list.append(item)
        return list

class MatchLiveModel(db.Model):
    __tablename__ = 'match_source'
    id = db.Column(db.Integer,primary_key=True)
    category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category_sub.sub_category_id'))
    match_id = db.Column(db.VARCHAR(80),db.ForeignKey('match.match_id'))
    match_source_1 = db.Column(db.String)
    match_type_1 = db.Column(db.String)
    def __init__(self,category_id,sub_category_id,match_id):
        self.category_id=  category_id
        self.sub_category_id = sub_category_id
        self.match_id = match_id
    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'password':
                continue
            else:
                result[key] = getattr(self, key)
        return result

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_match_id(cls,match_id):
        return cls.query.filter_by(match_id=match_id).first()
    