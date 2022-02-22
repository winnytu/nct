from db import db 
import json
from datetime import datetime
from sqlalchemy import desc,asc

class MainCategoryModel(db.Model):
    __tablename__= "category"
    id = db.Column(db.Integer,primary_key=True)
    category = db.Column(db.String)
    category_id = db.Column(db.String,unique=True)
    icon = db.Column(db.String,unique=True)
    article_status = db.Column(db.Integer,default=0)
    live_status = db.Column(db.Integer,default=0)
    match_status = db.Column(db.Integer,default=0)
    video_status = db.Column(db.Integer,default=0)
    sub_category_list = db.relationship('SubCategoryModel',lazy='dynamic')
    article_list =  db.relationship('ArticleModel',lazy='dynamic',backref='category')
    def __init__(self,category,category_id):
        self.category = category
        self.category_id = category_id
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

    @classmethod
    def find_all(cls):
        return cls.query.order_by(asc('category_id')).all()
    @classmethod
    def find_by_category(cls,category_id):
        return cls.query.filter_by(category_id=category_id).first()
    @classmethod
    def find_sub_category_list(cls,category_id):
        return [item.to_dict() for item in cls.query.filter_by(category_id=category_id).first().sub_category_list.order_by(('sub_category_id'))]
    @classmethod
    def find_all_article_list(cls,category_id,page,page_size):
        return [item.to_dict() for item in  cls.query.filter_by(category_id=category_id).first().article_list.order_by(desc('publish_date')).limit(page_size).offset((page*10)-10).all()]
    @classmethod
    def find_show_article_list(cls,category_id,page,page_size):
        result = []
        for item in cls.query.filter_by(category_id=category_id).first().article_list.order_by(desc('publish_date')).limit(page_size).offset((page*10)-10).all():
            if item.show_status == "1":
                newItem = item.to_dict()
                newItem['like'] = len(item.like_list)
                newItem['comment'] = len(item.comment_list)
                result.append(newItem) 
        return result

class SubCategoryModel(db.Model):
    __tablename__= "category_sub"
    id = db.Column(db.Integer,primary_key=True)
    category_id = db.Column(db.String,db.ForeignKey('category.category_id'))
    sub_category = db.Column(db.String)
    sub_category_id = db.Column(db.String,unique=True)
    icon = db.Column(db.String,unique=True)
    article_status = db.Column(db.Integer,default=0)
    live_status = db.Column(db.Integer,default=0)
    match_status = db.Column(db.Integer,default=0)
    video_status = db.Column(db.Integer,default=0)
    article_list =  db.relationship('ArticleModel',lazy='dynamic',backref="sub_category")
    rank_list = db.relationship('RankModel',backref='category')
    def __init__(self,category_id,sub_category,sub_category_id):
        self.category_id = category_id
        self.sub_category = sub_category
        self.sub_category_id = sub_category_id
    def to_dict(self): 
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
    def find_all(cls):
        return cls.query.order_by(asc('sub_category_id')).all()
    @classmethod
    def find_by_sub_category(cls,sub_category_id):
        return cls.query.filter_by(sub_category_id=sub_category_id).first()
    @classmethod
    def find_all_article_list(cls,sub_category_id,page,page_size):
        return [item.to_dict() for item in  cls.query.filter_by(sub_category_id=sub_category_id).first().article_list.order_by(desc('publish_date')).limit(page_size).offset((page*10)-10).all()]
    @classmethod
    def find_show_article_list(cls,sub_category_id,page,page_size):
        result = []
        for item in cls.query.filter_by(sub_category_id=sub_category_id).first().article_list.order_by(desc('publish_date')).limit(page_size).offset((page*10)-10).all():
            if item.show_status == "1":
                newItem = item.to_dict()
                newItem['like'] = len(item.like_list)
                newItem['comment'] = len(item.comment_list)
                result.append(newItem) 
        return result
    