import sqlite3
from db import db 
from datetime import datetime

class LikeModel(db.Model):
    __tablename__= "like"
    id = db.Column(db.Integer,primary_key=True)
    article_id = db.Column(db.String(200),db.ForeignKey('article.article_id'))
    comment_id = db.Column(db.String(200),db.ForeignKey('comment.comment_id'))
    user_id = db.Column(db.String(200),db.ForeignKey('member.user_id'))
    article = db.relationship('ArticleModel',overlaps="like_list")
    comment = db.relationship('CommentModel',overlaps="like_list")
    def __init__(self,user_id):
        self.user_id = user_id
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