#! /Users/winnytu/opt/anaconda3/envs/crawler/bin/python

import requests
import json
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import Column, String, Integer,create_engine,ForeignKey,ARRAY,DateTime
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
import traceback
import os

# 64位ID的划分
WORKER_ID_BITS = 5
DATACENTER_ID_BITS = 5
SEQUENCE_BITS = 12

# 最大取值计算
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

# 移位偏移计算
WOKER_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 序号循环掩码
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

# Twitter元年时间戳
TWEPOCH = 1288834974657


logger = logging.getLogger('flask.app')


class IdWorker(object):
    """
    用于生成IDs
    """

    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 其实序号
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id值越界')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id值越界')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_id(self):
        """
        获取新ID
        :return:
        """
        timestamp = self._gen_timestamp()

        # 时钟回拨
        if timestamp < self.last_timestamp:
            logging.error('clock is moving backwards. Rejecting requests until {}'.format(self.last_timestamp))
            raise

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
            (self.worker_id << WOKER_ID_SHIFT) | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:0815@localhost/sport168'
if os.environ.get('FLASK_ENV') == "heroku":
    SQLALCHEMY_DATABASE_URL = 'postgresql://bdyfqhhgdklldy:ed9829de1a13181f0be4c1ec1d59699a861e19af77d5731f9cc20ef86fef334c@ec2-54-147-76-191.compute-1.amazonaws.com/dhs4scpjlhik'
if os.environ.get('FLASK_ENV') == "development":
    SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:6NqLTvFAjJLJPKxo@database-dev.ci68ranogp85.ap-northeast-1.rds.amazonaws.com/topyl_dev'
if os.environ.get('FLASK_ENV') == "uat":
    SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:QyNxBfKgCuQs$FDD@database-uat.ci68ranogp85.ap-northeast-1.rds.amazonaws.com/topyl_uat'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = session()
class MainCategoryModel(Base):
    __tablename__= "category"
    id = Column(Integer,primary_key=True)
    category = Column(String)
    category_id = Column(String,unique=True)
    icon = Column(String,unique=True)
    article_status = Column(Integer,default=0)
    live_status = Column(Integer,default=0)
    match_status = Column(Integer,default=0)
    video_status = Column(Integer,default=0)
    sub_category_list = relationship('SubCategoryModel')
    article_list =  relationship('ArticleModel')
class SubCategoryModel(Base):
    __tablename__= "category_sub"
    id = Column(Integer,primary_key=True)
    category_id = Column(String,ForeignKey('category.category_id'))
    sub_category = Column(String)
    sub_category_id = Column(String,unique=True)
    icon = Column(String,unique=True)
    article_status = Column(Integer,default=0)
    live_status = Column(Integer,default=0)
    match_status = Column(Integer,default=0)
    video_status = Column(Integer,default=0)
    article_list =  relationship('ArticleModel')
class ArticleModel(Base):
    __tablename__ = 'article'
    id = Column(Integer,primary_key=True,autoincrement=True)
    article_id = Column(String,unique=True)
    creator = Column(String)
    title = Column(String)
    category_id = Column(String,ForeignKey('category.category_id'))
    sub_category_id = Column(String,ForeignKey('category_sub.sub_category_id'))
    cover_img =  Column(String)
    publish_date = Column(DateTime, default=datetime.now)
    click = Column(Integer,default=0)
    tag = Column(ARRAY(String))
    show_status = Column(String, default=1)
    reply_status = Column(String, default=1)
    created_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    content = Column(String)
    def __init__(self,title,category_id,sub_category_id,publish_date):
        self.title = title
        self.category_id=  category_id
        self.sub_category_id = sub_category_id
        self.publish_date = publish_date
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
        db.add(self)
        db.commit()
    @classmethod
    def find_by_id(cls,article_id):
        return db.query(ArticleModel).filter(ArticleModel.article_id == article_id).first()
    @classmethod
    def find_by_title(cls,title):
        return db.query(ArticleModel).filter(ArticleModel.title == title).first()

custom_headers = {
    'cache-control':'no-cache',
    'pragma':'no-cache',
    'referer':'https://live.qq.com/news',
}
user_agent_list = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
    'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Mobile Safari/537.36'
]
delay_choices = [0.8,0.5,1,0.3,0.7]

tabList = [
    {'tab':1,'category':1,'subCategory':11},
    {'tab':2,'category':1,'subCategory':12},
]
try :
    for tab in tabList:
        for page in range(1,20):
            searchTab = tab['tab']
            url = f"https://live.qq.com/api/web_news/news_index?tab={searchTab}&page={page}"
            custom_headers['User-Agent'] = random.choice(user_agent_list)
            match_resp = requests.get(url,headers=custom_headers)
            time.sleep(random.choice(delay_choices))
            match_resp.close()
            respList = json.loads(match_resp.text)['data']['list']
            for resp in respList:
                if  ArticleModel.find_by_title(resp['title']):
                    break;
                else:
                    new_article = {}
                    new_article['title'] = resp['title']
                    new_article['category_id'] = tab['category']
                    new_article['sub_category_id'] =  tab['subCategory']
                    new_article['publish_date'] = datetime.fromtimestamp(int(resp['publish_time']))
                    addNews = ArticleModel(**new_article)
                    addNews.save_to_db()
                    addNews.article_id = str(IdWorker(1,1,addNews.id).get_id())
                    addNews.cover_img= resp['cover_img'][0]['img_default']
                    addNews.update_time = datetime.fromtimestamp(int(resp['update_time']))
                    addNews.created_time = datetime.fromtimestamp(int(resp['update_time']))
                    addNews.creator = 'crawler'
                    newsId= resp['news_id']
                    content_url = f"https://live.qq.com/news/detail/{newsId}"
                    content_headers = {
                        'cache-control':'no-cache',
                        'pragma':'no-cache',
                        'referer':'https://live.qq.com/news/32',
                        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                    }
                    content_resp = requests.get(content_url,headers=content_headers)
                    time.sleep(0.5)
                    content_resp.close()
                    content_text = content_resp.text
                    soup = BeautifulSoup(content_text, 'html.parser')
                    content = str(soup.find(class_='__39VSG7Fp'))
                    addNews.content = content
                    addNews.save_to_db()
    print(str(datetime.now())+'完成新聞爬蟲')
except:
    traceback.print_exc()
