from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.banner import BannerModel
from models.category import MainCategoryModel
from models.article import ArticleModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import json
import requests

class HomeLive(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    def post(self):
        data = HomeInfo.parser.parse_args()
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=68&page=0&page_size=5"
        hot_resp = requests.get(url,headers=custom_headers)
        if json.loads(hot_resp.text)['data']:
            hot_result = json.loads(hot_resp.text)['data'][0]['rooms'][:5]
        else:
            hot_result = []
        url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=72&page=0&page_size=5"
        basketball_resp = requests.get(url,headers=custom_headers)
        if json.loads(basketball_resp.text)['data']:
            basketball_result = json.loads(basketball_resp.text)['data'][0]['rooms'][:5]
        else:
            basketball_result = []
        url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=71&page=0&page_size=5"
        soccer_resp = requests.get(url,headers=custom_headers)
        if json.loads(soccer_resp.text)['data']:
            soccer_result = json.loads(soccer_resp.text)['data'][0]['rooms'][:5]
        else:
            soccer_result = []
        url = f"http://api.rtoieurvoncenter.xyz/v1/web/plate/schedule"
        match_resp = requests.get(url,headers=custom_headers)
        return {
            'status':'success',
            'body':{
                'match':json.loads(match_resp.text)['data']['match_list'],
                'hotLiveList':hot_result,
                'basketballLiveList':basketball_result,
                'soccerLiveList':soccer_result,
            }
        }, 200

class HomeInfo(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    def post(self):
        banner_list = BannerModel.find_by_show('home')
        basketball_news = MainCategoryModel.find_show_article_list('1',1,5)
        soccer_news = MainCategoryModel.find_show_article_list('2',1,5)
        hot_news = ArticleModel.host_article()
        return {
            'status':'success',
            'body':{
                'hotNewsList':hot_news,
                'basketballNewsList':basketball_news,
                'soccerNewsList':soccer_news,
            }
        }, 200