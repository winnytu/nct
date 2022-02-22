from db import db 
import json
from datetime import datetime, timedelta,date
import time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import asc,desc

class ArticleModel(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    article_id = db.Column(db.String,unique=True)
    creator = db.Column(db.String)
    title = db.Column(db.VARCHAR(80))
    category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category_sub.sub_category_id'))
    cover_img =  db.Column(db.VARCHAR)
    publish_date = db.Column(db.DateTime, default=datetime.now)
    click = db.Column(db.Integer,default=0)
    tag = db.Column(ARRAY(db.String))
    show_status = db.Column(db.VARCHAR, default=1)
    reply_status = db.Column(db.VARCHAR, default=1)
    created_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    content = db.Column(db.VARCHAR)
    like_list = db.relationship('LikeModel')
    comment_list = db.relationship('CommentModel')
    def __init__(self,title,category_id,sub_category_id,publish_date):
        self.title = title
        self.category_id=  category_id
        self.sub_category_id = sub_category_id
        self.publish_date = publish_date
    # 配合to_dict一起使用
    def to_json(self, all_vendors):  # 多条结果时转为list(json)
        v = [ven.to_dict() for ven in all_vendors]
        return v
    def to_dict(self):  # 方法二，该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime: 
                result[key] = getattr(self, key).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'id':
                continue
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
    def find_by_id(cls,article_id):
        return cls.query.filter_by(article_id=article_id).first()
    @classmethod
    def host_article(cls):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        list = []
        item_list = cls.query.filter(cls.publish_date>today).filter(cls.publish_date<tomorrow).filter(cls.show_status != "0").order_by(desc('click')).limit(5).all()
        print(len(item_list))
        for item in cls.query.filter(cls.publish_date>today).filter(cls.publish_date<tomorrow).filter(cls.show_status != "0").order_by(desc('click')).limit(5).all():
            newItem = item.to_dict()
            newItem['comment'] = len(item.comment_list)
            newItem['like'] = len(item.like_list)
            list.append(newItem)
        if len(item_list) < 5:
            num = 5 - len(item_list)
            past = today - timedelta(days= 7)
            for item in cls.query.filter(cls.publish_date>past).filter(cls.publish_date<today).filter(cls.show_status != "0").order_by(desc('publish_date')).limit(num).all():
                newItem = item.to_dict()
                newItem['comment'] = len(item.comment_list)
                newItem['like'] = len(item.like_list)
                list.append(newItem)
        return list