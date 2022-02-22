from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.match import MatchModel,MatchLiveModel
from models.category import MainCategoryModel,SubCategoryModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
import random
from datetime import datetime
from idGenerator import IdWorker
from sqlalchemy import desc,asc

class MatchCrawler(Resource):
    def post(self):
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
            'imei':'7fd6a886eb5e88bd81154e0224f4608f',
        }
        user_agent_list = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
        ]
        delay_choices = [0.8, 0.5, 1,0.3]
        tabList = [
            # 籃球
            # nba
            {'sport_id':2,'event_id':1,'category':1,'subCategory':11},
            # cba
            {'sport_id':2,'event_id':3,'category':1,'subCategory':12},
            # 足球
            # 西甲
            {'sport_id':1,'event_id':12,'category':1,'subCategory':21},
            # 意甲
            {'sport_id':1,'event_id':10,'category':1,'subCategory':22},
            # 德甲
            {'sport_id':1,'event_id':129,'category':1,'subCategory':22},

        ]
        date_url = 'http://api.rtoieurvoncenter.xyz/v161/matchs/date?event_id={eventId}&sport_id={sportId}'
        schedule_url = 'http://api.rtoieurvoncenter.xyz/h5/v13/event/matchs?page=0&page_size=50&page_type=1&event_id={eventId}&sport_id={sportId}'
        try :
            for tab in tabList:
                eventId = tab['event_id']
                sportId = tab['sport_id']
                date_url = f'http://api.rtoieurvoncenter.xyz/v161/matchs/date?event_id={eventId}&sport_id={sportId}'
                custom_headers['User-Agent'] = random.choice(user_agent_list)
                date_resp = requests.get(date_url,headers=custom_headers)
                date_resp.close()
                time.sleep(random.choice(delay_choices))
                dateList = json.loads(date_resp.text)['data']
                for date in dateList:
                    dateTime = date['match_date']
                    schedule_url =f'http://api.rtoieurvoncenter.xyz/v161/matchs/list?date_time={dateTime}&event_id={eventId}&sport_id={sportId}'
                    custom_headers['User-Agent'] = random.choice(user_agent_list)
                    schedule_resp = requests.get(schedule_url,headers=custom_headers)
                    schedule_list= json.loads(schedule_resp.text)['data'][0]['match_list']
                    for schedule in schedule_list[:3]:
                        is_match = MatchLiveModel.query.filter_by(match_source_1= str(schedule['match_id'])).first()
                        if is_match:
                            match_item = MatchModel.find_by_match_id(is_match.match_id)
                            match_item.category_id = tab['category']
                            match_item.sub_category_id =  tab['subCategory']
                            match_item.match_date = json.loads(schedule_resp.text)['data'][0]['date']
                            match_item.match_time = datetime.fromtimestamp(int(schedule['match_time']))
                            match_item.match_status = schedule['match_status']
                            match_item.match_hour = schedule['match_hour']
                            match_item.home_name = schedule['home_name']
                            match_item.home_logo = schedule['home_logo']
                            match_item.home_score = schedule['home_score']
                            match_item.away_name = schedule['away_name']
                            match_item.away_logo = schedule['away_logo']
                            match_item.away_score = schedule['away_score']
                            match_item.stage_name= schedule['stages_name']
                            match_item.save_to_db()
                        else:
                            new_schedule = {}
                            new_schedule['category_id'] = tab['category']
                            new_schedule['sub_category_id'] =  tab['subCategory']
                            new_schedule['match_date'] = json.loads(schedule_resp.text)['data'][0]['date']
                            new_schedule['match_time'] = datetime.fromtimestamp(int(schedule['match_time']))
                            new_schedule['match_status'] = schedule['match_status']
                            match = MatchModel(**new_schedule)
                            match.save_to_db()
                            match.match_id = str(IdWorker(1,3,match.id).get_id())
                            match.match_hour = schedule['match_hour']
                            match.home_name = schedule['home_name']
                            match.home_logo = schedule['home_logo']
                            match.home_score = schedule['home_score']
                            match.away_name = schedule['away_name']
                            match.away_logo = schedule['away_logo']
                            match.away_score = schedule['away_score']
                            match.stage_name= schedule['stages_name']
                            match.save_to_db()
                            match_live = MatchLiveModel(tab['category'],tab['subCategory'],match.match_id)
                            match_live.save_to_db()
                            match_live.match_source_1 = schedule['match_id']
                            match_live.match_type_1 = schedule['sport_id']
                            match_live.save_to_db()
                        schedule_resp.close()
                        time.sleep(random.choice(delay_choices))
            return {'status':'success','body':'爬蟲成功'}
        except Exception as e:
            print (e)
            return {'status':'success','body':'爬蟲失敗'}

class GetMatchTab(Resource):
    def post(self):
        mainTab = MainCategoryModel.query.filter(MainCategoryModel.match_status!=0).order_by(asc('match_status')).all()
        tabList = []
        for main in mainTab:
            mainList = main.to_dict()
            list = []
            for tab in SubCategoryModel.query.filter_by(category_id=main.category_id).filter(SubCategoryModel.match_status!=0).order_by(asc('match_status')).all():
                tab_new = tab.to_dict()
                # print(tab.sub_category_id)
                # a = MatchModel.find_by_match_today(tab.sub_category_id)
                tab_new['today'] = MatchModel.find_by_match_today(tab.sub_category_id)
                list.append(tab_new)
            mainList['subTabList'] = list
            tabList.append(mainList)
        return {'status':'success','body':tabList}

class GetMatchEventSchedule(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category_id',
        type = str,
        required = False,
        help = "請填寫category_id"
    )
    parser.add_argument('sub_category_id',
        type = str,
        required = False,
        help = "請填寫sub_category_id"
    )
    def post(self):
        # 籃球 sport_id=2 足球 sport_id=1
        # date_time 日期秒數
        data = request.get_json()
        category_id = data.get('category_id')
        sub_category_id = data.get('sub_category_id')
        if category_id:
            list =  MatchModel.find_by_category_id(category_id)
        else:
            list =  MatchModel.find_by_sub_category_id(sub_category_id)
        return {'status':'success','body':list}


class GetMatchRoomList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('match_id',
        type = str,
        required = True,
        help = "請填寫match_id"
    )
    parser.add_argument('User-Agent', location='headers')
    def post(self):
        data = GetMatchRoomList.parser.parse_args()
        match = MatchLiveModel.find_by_match_id(data['match_id'])
        sportId = match.match_type_1
        matchId = match.match_source_1
        url = f"http://api.rtoieurvoncenter.xyz/h5/v13/match/live?match_id={matchId}&page=0&page_size=18&sport_id={sportId}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetMatchLive(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('roomId',type = str,required = True, help = "請填寫roomId")
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    def post(self):
        data = GetMatchLive.parser.parse_args()
        roomId = data['roomId']
        sportId = data['sportId']
        matchId = data['matchId']
        url = f"http://api.rtoieurvoncenter.xyz/v1/room?room_id={roomId}&sport_id={sportId}&match_id={matchId}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        resp = json.loads(match_resp.text)
        return {'status':'success','body':resp}

class GetMatchStat(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    def post(self):
        data = GetMatchStat.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/outs?match_id={matchId}&sport_id={sportId}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetTeamAnalyze(Resource):
    #聯賽積分 #場均數據
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    def post(self):
        data = GetTeamAnalyze.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/goal?match_id={matchId}&sport_id={sportId}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}


class GetTeamHistory(Resource):
    #歷史交鋒
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    # 1 五場 2 10場 3 15場 4 20場
    parser.add_argument('pageType',type = str,required = True, help = "請填寫pageType")
    # 0:未篩選 1:同主客 
    parser.add_argument('teamType',type = str,required = True, help = "請填寫teamType")
    def post(self):
        data = GetTeamHistory.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        pageType = data['pageType']
        teamType = data['teamType']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/history?match_id={matchId}&sport_id={sportId}&type_team={teamType}&type_screen={pageType}&type_event=0"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        print(json.loads(match_resp.text))
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetHomeHistory(Resource):
    #主場戰績
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    # 1 五場 2 10場 3 15場 4 20場
    parser.add_argument('pageType',type = str,required = True, help = "請填寫pageType")
    # 0:未篩選 1:同主客 
    parser.add_argument('teamType',type = str,required = True, help = "請填寫teamType")
    # 0:未篩選 1:同賽事
    parser.add_argument('matchType',type = str,required = True, help = "請填寫matchype")
    def post(self):
        data = GetHomeHistory.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        pageType = data['pageType']
        teamType = data['teamType']
        matchType = data['matchType']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/home/record?match_id={matchId}&sport_id={sportId}&type_team={teamType}&type_screen={pageType}&type_event={matchType}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetAwayHistory(Resource):
    #客場戰績
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    # 1 五場 2 10場 3 15場 4 20場
    parser.add_argument('pageType',type = str,required = True, help = "請填寫pageType")
    # 0:未篩選 1:同主客 
    parser.add_argument('teamType',type = str,required = True, help = "請填寫teamType")
    # 0:未篩選 1:同賽事
    parser.add_argument('matchType',type = str,required = True, help = "請填寫matchype")
    def post(self):
        data = GetAwayHistory.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        pageType = data['pageType']
        teamType = data['teamType']
        matchType = data['matchType']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/away/record?match_id={matchId}&sport_id={sportId}&type_team={teamType}&type_screen={pageType}&type_event={matchType}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetWinStat(Resource):
    #勝分差
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    # 0:未篩選 1:同主客 
    parser.add_argument('teamType',type = str,required = True, help = "請填寫teamType")
    # 1:勝 2:負
    parser.add_argument('winType',type = str,required = True, help = "請填寫winType")
    def post(self):
        data = GetWinStat.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        teamType = data['teamType']
        winType = data['winType']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/win?match_id={matchId}&sport_id={sportId}&type_win={winType}&type_team={teamType}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}

class GetResultStat(Resource):
    #半全場勝負
    parser = reqparse.RequestParser()
    parser.add_argument('User-Agent', location='headers')
    parser.add_argument('sportId',type = str,required = True, help = "請填寫sportId")
    parser.add_argument('matchId',type = str,required = True, help = "請填寫matchId")
    # 0:未篩選 1:同主客 
    parser.add_argument('teamType',type = str,required = True, help = "請填寫teamType")
    # 0:未篩選 1:同賽事
    parser.add_argument('matchType',type = str,required = True, help = "請填寫matchype")
    def post(self):
        data = GetResultStat.parser.parse_args()
        sportId = data['sportId']
        matchId = data['matchId']
        teamType = data['teamType']
        matchType = data['matchType']
        url = f"http://api.rtoieurvoncenter.xyz/v15/matchs/game?match_id={matchId}&sport_id={sportId}&type_team={teamType}&type_event={matchType}"
        custom_headers = {
            'host':'api.rtoieurvoncenter.xyz',
            'cache-control':'no-cache',
            'origin':'http://m.rrty11.com',
            'pragma':'no-cache',
            'referer':'http://m.rrty11.com/',
        }
        custom_headers['User-Agent'] = data['User-Agent']
        match_resp = requests.get(url,headers=custom_headers)
        # resp = json.loads(match_resp.text)['data']
        # return {'status':'success','body':resp}