from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
from models.category import SubCategoryModel
import requests
import json
import random
from sqlalchemy import desc,asc

class GetLiveTab(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    def post(self):
        data = GetLiveTab.parser.parse_args()
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',       
        }
        url = 'http://api.rtoieurvoncenter.xyz/v14/channel/list'
        custom_headers['User-Agent'] = data['User-Agent']
        resp = requests.get(url,headers=custom_headers)
        tabList = json.loads(resp.text)['data']
        return {'status':'success','body':tabList}
        # tabList = SubCategoryModel.query.filter(SubCategoryModel.live_status!=0).order_by(asc('live_status')).all()
        # return {'status':'success','body':[tab.to_dict() for tab in tabList]}

class GetLiveList(Resource):
    def post(self):
        data = request.get_json()
        channel_id=data['channelId']
        page = data['page']
        page_size = data['pageSize']
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
            'imei':'7fd6a886eb5e88bd81154e0224f4608f',
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        }
        if channel_id == 68:
            url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=68&page=0&page_size=5"
            match_resp = requests.get(url,headers=custom_headers)
            if json.loads(match_resp.text)['data']:
                match_result = json.loads(match_resp.text)['data'][0]['rooms']
            else:
                match_result = []
            url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=71&page=0&page_size=5"
            basketball_resp = requests.get(url,headers=custom_headers)
            if json.loads(basketball_resp.text)['data']:
                basketball_result = json.loads(basketball_resp.text)['data'][0]['rooms']
            else:
                basketball_result = []
            url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id=72&page=0&page_size=5"
            soccer_resp = requests.get(url,headers=custom_headers)
            if json.loads(soccer_resp.text)['data']:
                soccer_result = json.loads(soccer_resp.text)['data'][0]['rooms']
            else:
                soccer_result = []
            return {'status':'success','body':{'hotList':match_result,'basketballList':basketball_result,'soccerList':soccer_result}}
        else:
        # 推薦 channel_id=68 籃球 channel_id=71 足球 channel_id=72
            url = f"http://api.rtoieurvoncenter.xyz/v14/live/getlist?channel_id={channel_id}&page={page}&page_size={page_size}"
            match_resp = requests.get(url,headers=custom_headers)
            if json.loads(match_resp.text)['data']:
                return {'status':'success','body':{'hotList':json.loads(match_resp.text)['data'][0]['rooms']}}
            else: 
                return {'status':'success','body':{'hotList':[]}}

