import sqlite3
from db import db 
from datetime import datetime,time
from sqlalchemy import asc,desc

class CommentModel(db.Model):
    __tablename__= "comment"
    id = db.Column(db.Integer,primary_key=True)
    comment_id = db.Column(db.String,unique=True)
    article_id = db.Column(db.String,db.ForeignKey('article.article_id'))
    user_id = db.Column(db.String,db.ForeignKey('member.user_id')) 
    reply_id = db.Column(db.String,db.ForeignKey('comment.comment_id'))
    comment  = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.now)
    like_list = db.relationship('LikeModel')
    def __init__(self,article_id,user_id,comment):
        self.article_id = article_id
        self.user_id = user_id
        self.comment = comment
    def to_dict(self): 
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
    def find_by_article(cls,article_id,user_id):
        comment_list = []
        for comment in  cls.query.filter_by(article_id=article_id).order_by(desc('created_date')).all():
            if comment.reply_id is None:
                item = comment.to_dict()
                sub_item_list = []
                for sub in cls.query.filter_by(reply_id=comment.comment_id).order_by(desc('created_date')).all():
                    sub_item = sub.to_dict()
                    sub_item['commenter'] = {'user_name':sub.commenter.user_name,'avatar':sub.commenter.avatar}
                    sub_item['like'] = len(sub.like_list)
                    sub_item['isLike'] = 0 
                    if user_id:
                        for like in sub.like_list:
                            if like.user_id == user_id: 
                                sub_item['isLike'] = 1
                    sub_item_list.append(sub_item)
                item['relatedComment'] = sub_item_list
                item['commenter'] = {'user_name':comment.commenter.user_name,'avatar':comment.commenter.avatar}
                item['like'] = len(comment.like_list)
                item['isLike'] = 0 
                if user_id:
                    for like in comment.like_list:
                        like.user_id == user_id 
                        item['isLike'] = 1
                comment_list.append(item)
        return comment_list