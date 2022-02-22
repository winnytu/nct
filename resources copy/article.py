from flask import jsonify
from sqlalchemy.sql.sqltypes import Boolean, Integer
from sqlalchemy import desc,asc,and_,or_
from flask_restful import Resource,reqparse,request,fields,marshal
from models.article import ArticleModel
from models.category import MainCategoryModel,SubCategoryModel
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from idGenerator import IdWorker
from imageSave import ImageSave

class ArticleCrawler(Resource):
    def post(self):
        custom_headers = {
            'cache-control':'no-cache',
            'pragma':'no-cache',
            'referer':'https://live.qq.com/news/32',
        }
        user_agent_list = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
        ]
        delay_choices = [0.8, 0.5, 1,0.3]
        tabList = [
                    {'tab':1,'category':1,'subCategory':11},
                    {'tab':2,'category':1,'subCategory':12},
                    {'tab':20,'category':2,'subCategory':21},
                    {'tab':21,'category':2,'subCategory':22},
                    {'tab':22,'category':2,'subCategory':23},
                    {'tab':23,'category':2,'subCategory':24},
                    {'tab':24,'category':2,'subCategory':25},
                    {'tab':26,'category':2,'subCategory':27},
                    {'tab':27,'category':2,'subCategory':26},
                    {'tab':51,'category':3,'subCategory':31},
                    {'tab':53,'category':4,'subCategory':41},
                ]
        try :
            for tab in tabList:
                for page in range(1,2):
                    searchTab = tab['tab']
                    url = f"https://live.qq.com/api/web_news/news_index?tab={searchTab}&page={page}"
                    custom_headers['User-Agent'] = random.choice(user_agent_list)
                    match_resp = requests.get(url,headers=custom_headers)
                    time.sleep(random.choice(delay_choices))
                    match_resp.close()
                    respList = json.loads(match_resp.text)['data']['list']
                    for resp in respList:
                        if  ArticleModel.query.filter(ArticleModel.title == resp['title'] ).first():
                            break;
                        else:
                            new_article = {}
                            new_article['title'] = resp['title']
                            new_article['category_id'] = tab['category']
                            new_article['sub_category_id'] =  tab['subCategory']
                            new_article['publish_date'] = datetime.fromtimestamp(int(resp['publish_time']))
                            addNews = ArticleModel(**new_article)
                            addNews.save_to_db()
                            addNews.article_id = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))+ str(IdWorker(1,1,addNews.id).get_id())[-6:]
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
                        
            return {'status':'success','body':'成功'}
        except:
            return {'status':'success','body':'失敗'}

class GetArticleTab(Resource):
    def post(self):
        tabList = SubCategoryModel.query.filter(SubCategoryModel.article_status!=0).order_by(asc('article_status')).all()
        return {'status':'success','body':[tab.to_dict() for tab in tabList]}

class GetArticleList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category',
        type = str,
        required = True,
        help = "請填寫分類id"
    )
    parser.add_argument('subCategory',
        type = str,
        required = True,
        help = "請填寫分類id"
    )
    parser.add_argument('page',
        type = int,
        required = False,
        help = "請填寫頁數",
        default=1
    )
    parser.add_argument('pageSize',
        type = int,
        required = False,
        help = "請填寫page size",
        default=10
    )
    def post(self):
        data = GetArticleList.parser.parse_args()
        if data['subCategory'] == "10" or data['subCategory'] == "20" or data['subCategory'] == "30" or data['subCategory'] == "40":
            list = MainCategoryModel.find_show_article_list(data['category'],data['page'],data['pageSize'])
        else:
            list = SubCategoryModel.find_show_article_list(data['subCategory'],data['page'],data['pageSize'])
        return {'status':'success','body':list}

class GetAllArticleList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('page',
        type = int,
        required = False,
        help = "請填寫頁數",
        default = 1
    )
    parser.add_argument('pageSize',
        type = int,
        required = False,
        help = "請填寫page size",
        default  = 10
    )
    def post(self):
        data = GetAllArticleList.parser.parse_args()
        list = []
        total = ArticleModel.query.count()
        crawler = ArticleModel.query.filter(ArticleModel.creator == 'crawler').count()
        for item in ArticleModel.query.order_by(desc('publish_date')).limit(data['pageSize']).offset((data['page']*10)-10).all():
            article = item.to_dict()
            article['category'] = item.category.category
            article['subCategory'] = item.sub_category.sub_category
            article['like'] = len(item.like_list)
            article['comment'] = len(item.comment_list)
            list.append(article)
        return {'status':'success','body':{'articleList':list,'total':total,'crawler':crawler}}

class GetArticleDetail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('articleId',
        type = str,
        required = True,
        help = "請填寫新聞id"
    )
    parser.add_argument('userId',
        type = str,
        required = False,
        help = "請填寫用戶id"
    )
    parser.add_argument('superUser',
        type = str,
        required = False,
        help = "請填寫用戶id"
    )
    def post(self):
        data = GetArticleDetail.parser.parse_args()
        article = ArticleModel.find_by_id(data['articleId'])
        if data['superUser'] is None:
            click_num = article.click 
            article.click = click_num + 1
            article.save_to_db()
        article_resp = article.to_dict()
        article_resp['like'] = len(article.like_list)
        article_resp['comment'] = len(article.comment_list)
        article_resp['isLike'] = 0
        article_resp['sub_category'] =SubCategoryModel.find_by_sub_category(article.sub_category_id).to_dict()['sub_category']
        if data['userId']:
            for like in  article.like_list:
                if like.user_id == data['userId']:
                    article_resp['isLike'] = 1
                    break
        return {'status':'success','body': article_resp}

class ToggleArticleShowStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('idList',
        type = str,
        action='append',
        required = True,
        help = "請填寫id"
    )
    parser.add_argument('showStatus',
        type = str,
        required = True,
        help = "請填寫id"
    )
    def post(self):
        data =ToggleArticleShowStatus.parser.parse_args()
        for id in data['idList']:
            article = ArticleModel.find_by_id(id)
            article.show_status = data['showStatus']
            article.save_to_db()
        return {'status':'success','body': '狀態更新成功'}

class ToggleArticleReplyStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('idList',
        type = str,
        action='append',
        required = True,
        help = "請填寫id"
    )
    parser.add_argument('replyStatus',
        type = str,
        required = True,
        help = "請填寫狀態"
    )
    def post(self):
        data = ToggleArticleReplyStatus.parser.parse_args()
        for id in data['idList']:
            article = ArticleModel.find_by_id(id)
            article.reply_status = data['replyStatus']
            article.save_to_db()
        return {'status':'success','body': '狀態更新成功'}

class GetHotArticleList(Resource):
    def post(self):
        list = ArticleModel.host_article()
        return {'status':'success','body':list}

class EditArticle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('article_id',
        type = str,
        required = False,
    )
    parser.add_argument('title',
        type = str,
        required = True,
        help = "請填寫title"
    )
    parser.add_argument('category_id',
        type = str,
        required = True,
        help = "請填寫運種id"
    )
    parser.add_argument('sub_category_id',
        type = str,
        required = True,
        help = "請填寫賽事id"
    )
    parser.add_argument('publish_date',
        type = str,
        required = True,
        help = "請填寫發佈日期"
    )
    parser.add_argument('cover_img',
        type = str,
        required = False,
    )
    parser.add_argument('content',
        type = str,
        required = False,
    )
    parser.add_argument('tag',type=str,action='append',help="請填寫分類")
    def post(self):
        data = EditArticle.parser.parse_args()
        if data['article_id']:
            article = ArticleModel.find_by_id(data['article_id'])
            article.title = data['title']
            article.category_id = data['category_id']
            article.sub_category_id = data['sub_category_id']
            article.publish_date = data['publish_date']
            article.tag = data['tag']
            article.content = data['content']
            img = ImageSave(article.article_id,data['cover_img'],'article').ImageSave()
            article.cover_img = img
            article.save_to_db()
        else:
            article = ArticleModel(data['title'],data['category_id'],data['sub_category_id'],data['publish_date'])
            article.save_to_db()
            article.article_id = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))+ str(IdWorker(1,1,article.id).get_id())[-6:]
            article.content = data['content']
            article.tag = data['tag']
            article.show_status = 0
            img = ImageSave(article.article_id,data['cover_img'],'article').ImageSave()
            article.cover_img = img
            article.save_to_db()
        return {'status':'success','body':article.to_dict()}

class DeleteArticle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('idList',
        type = str,
        action='append',
        required = True,
        help = "請填寫id"
    )
    def post(self):
        data = DeleteArticle.parser.parse_args()
        for id in data['idList']:
            article = ArticleModel.find_by_id(id)
            article.delete_from_db()
        return {'status':'success','body':'刪除成功'}

class SearchArticle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('keyword',
        type = str,
        required = True,
        help = "請輸入關鍵字"
    )
    def post(self):
        data = SearchArticle.parser.parse_args()
        keyword = data['keyword']
        category_result = SubCategoryModel.query.filter(SubCategoryModel.sub_category.like("%" + keyword + "%")).all()
        all_results = ArticleModel.query.filter(
            or_(
                ArticleModel.title.like("%" + keyword + "%"),
                ArticleModel.content.like("%" + keyword + "%"),
                ArticleModel.sub_category_id.in_([category_id.to_dict()['sub_category_id'] for category_id in category_result])
            )
        ).all()
        return {
            'status':'success',
            'body':[result.to_dict() for result in all_results]
        }, 200