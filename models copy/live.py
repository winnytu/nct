from db import db 
import json
from datetime import datetime, timedelta,date
import time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import asc,desc

class LiveroomModel(db.Model):
    __tablename__ = 'liveroom'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    liveroom_id = db.Column(db.String,unique=True)
    category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.VARCHAR(80),db.ForeignKey('category_sub.sub_category_id'))
    match_id = db.Column(db.VARCHAR(80),db.ForeignKey('match.match_id'))
    liveroom_title = db.Column(db.VARCHAR(80))
    liveroom_img =  db.Column(db.VARCHAR)
    host = db.Column(db.String)
    host_img = db.Column(db.String)
    liveroom_info = db.Column(db.String)
    pull_url = db.Column(db.String)
    liveroom_status = db.Column(db.String)
    remark = db.Column(db.String)
    show_status = db.Column(db.VARCHAR, default=1)
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
        for item in cls.query.filter(cls.publish_date>today).filter(cls.publish_date<tomorrow).filter(cls.show_status != "0").order_by(desc('click')).limit(5).all():
            newItem = item.to_dict()
            newItem['comment'] = len(item.comment_list)
            newItem['like'] = len(item.like_list)
            list.append(newItem)
        return list