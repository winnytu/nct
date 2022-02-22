from db import db 
import json
from datetime import datetime
from sqlalchemy import desc,asc,cast,Float
from itertools import groupby
from operator import attrgetter
from models.category import SubCategoryModel

class RankModel(db.Model):
    __tablename__= "stat_rank"
    id = db.Column(db.Integer,primary_key=True)
    category_id = db.Column(db.String,db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.String,db.ForeignKey('category_sub.sub_category_id'))
    team_name = db.Column(db.String)
    logo = db.Column(db.String)
    rank = db.Column(db.Integer)
    win = db.Column(db.Integer)
    loss = db.Column(db.Integer)
    points = db.Column(db.Integer)
    win_rate = db.Column(db.String)
    # 連勝/敗
    streaks = db.Column(db.String)
    # 籃板
    rebounds = db.Column(db.String)
    # 平均得分
    points_avg = db.Column(db.String)
    # 助攻
    assists = db.Column(db.String)
    # 投籃命中率
    field_goals_accuracy =  db.Column(db.String)
    # 三分命中率
    three_pointers_accuracy = db.Column(db.String)
    # 罚球命中率
    free_throws_accuracy = db.Column(db.String)
    ranking_name = db.Column(db.String)
    def __init__(self,rank,category_id,sub_category_id,team_name,win,loss,ranking_name):
        self.rank = rank
        self.category_id = category_id
        self.sub_category_id = sub_category_id
        self.team_name = team_name
        self.win = win
        self.loss = loss
        self.ranking_name = ranking_name
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
    def find_by_team(cls,team_name,sub_category_id):
        return cls.query.filter_by(team_name=team_name).filter_by(sub_category_id=sub_category_id).first()
    @classmethod
    def find_by_sub_category_id(cls,sub_category_id):
        lists = cls.query.filter_by(sub_category_id=sub_category_id).order_by('ranking_name',asc('rank')).all()
        groups = []
        for k, g in groupby(lists, attrgetter('ranking_name')):
            groups.append({'ranking_name':k,'list':[item.to_dict() for item in list(g)]})    
        return groups
    @classmethod
    def find_by_all(cls):
        lists = cls.query.order_by('sub_category_id','ranking_name',asc('rank')).all()
        groups = []
        for k, g in groupby(lists, attrgetter('sub_category_id')):
            rank = {}
            rank['sub_category_id'] = k
            rank['sub_category'] = SubCategoryModel.find_by_sub_category(k).sub_category
            rank_list = []
            for i, j in groupby(list(g), attrgetter('ranking_name')):
                rank_list.append({'ranking_name':i,'list':[item.to_dict() for item in list(j)]})    
            rank['rankList'] = rank_list
            if k == '11' or k == '12':
                rank['points'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(k).order_by(desc((cast(BasketballPlayerModel.points_avg,Float)))).limit(10).all()]
                rank['rebounds'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(k).order_by(desc((cast(BasketballPlayerModel.rebounds,Float)))).limit(10).all()]
                rank['assists'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(k).order_by(desc((cast(BasketballPlayerModel.assists,Float)))).limit(10).all()]
            else:
                rank['shooter'] = [list.to_dict() for list in StatPlayerModel.find_by_sub_category_id(k,'射手榜')]
                rank['assists'] = [list.to_dict() for list in StatPlayerModel.find_by_sub_category_id(k,'助攻榜')]
            groups.append(rank)    
        return groups
    @classmethod
    def find_by_ranking_name(cls,ranking_name):
        return cls.query.filter_by(ranking_name=ranking_name).order_by(asc('rank')).all()



class StatPlayerModel(db.Model):
    __tablename__= "stat_player"
    id = db.Column(db.Integer,primary_key=True)
    category_id = db.Column(db.String,db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.String,db.ForeignKey('category_sub.sub_category_id'))
    team_name = db.Column(db.String)
    team_logo = db.Column(db.String)
    rank = db.Column(db.Integer)
    player = db.Column(db.String)
    player_img = db.Column(db.String)
    # 分數
    points =  db.Column(db.String)
    ranking_name = db.Column(db.String)
    def __init__(self,rank,category_id,sub_category_id,team_name,team_logo,player,player_img,points,ranking_name):
        self.rank = rank
        self.category_id = category_id
        self.sub_category_id = sub_category_id
        self.team_name = team_name
        self.team_logo = team_logo
        self.player = player
        self.player_img = player_img
        self.ranking_name = ranking_name
        self.points = points
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
    def find_by_sub_category_id(cls,sub_category_id,ranking_name):
        return cls.query.filter_by(sub_category_id=sub_category_id).filter_by(ranking_name=ranking_name).order_by(asc('rank')).all()


class BasketballPlayerModel(db.Model):
    __tablename__= "stat_player_basketball"
    id = db.Column(db.Integer,primary_key=True)
    category_id = db.Column(db.String,db.ForeignKey('category.category_id'))
    sub_category_id = db.Column(db.String,db.ForeignKey('category_sub.sub_category_id'))
    team_name = db.Column(db.String)
    team_logo = db.Column(db.String)
    player = db.Column(db.String)
    player_img = db.Column(db.String)
    # 籃板
    rebounds = db.Column(db.String)
    # 平均得分
    points_avg = db.Column(db.String)
    # 助攻
    assists = db.Column(db.String)
    def __init__(self,category_id,sub_category_id,team_name,team_logo,player,player_img,rebounds,points_avg,assists):
        self.category_id = category_id
        self.sub_category_id = sub_category_id
        self.team_name = team_name
        self.team_logo = team_logo
        self.player = player
        self.player_img = player_img
        self.rebounds = rebounds
        self.points_avg = points_avg
        self.assists = assists
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
    def find_by_player(cls,player):
        return cls.query.filter_by(player=player).first()
    @classmethod
    def find_by_sub_category_id(cls,sub_category_id):
        return cls.query.filter_by(sub_category_id=sub_category_id)