from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.stat import RankModel,StatPlayerModel,BasketballPlayerModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
import random
import traceback
from datetime import datetime
from sqlalchemy import desc,asc,cast,Float
from bs4 import BeautifulSoup

class CBAcrawler(Resource):
    def post(self):
        try :
            rank_url = 'http://cbadata.sports.sohu.com/ranking/teams_detail'
            response = requests.get(rank_url)
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("div",class_="cutE").find("table").find_all("tr")[1:]
            for result_item in result: 
                stat_item = {}
                stat_item['rank'] =result_item.find_all('td')[0].string
                stat_item['category_id'] = 1
                stat_item['sub_category_id'] = 12
                stat_item['team_name'] = result_item.find_all('td')[1].a.string
                stat_item['win'] = result_item.find_all('td')[3].string
                stat_item['loss'] = result_item.find_all('td')[4].string
                stat_item['ranking_name'] = 'CBA常規賽'
                stat = RankModel(**stat_item)
                stat.win_rate = result_item.find_all('td')[5].string
                stat.save_to_db()
            data_url = 'http://cbadata.sports.sohu.com/ranking/teams/'
            response = requests.get(data_url)
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("div",class_="cutM").find_all("tr")[2:]
            for result_item in result: 
                stat_item = RankModel.find_by_team(result_item.find_all('td')[1].a.string,'12')
                stat_item.field_goals_accuracy=  result_item.find_all('td')[4].string
                stat_item.three_pointers_accuracy=  result_item.find_all('td')[7].string
                stat_item.free_throws_accuracy=  result_item.find_all('td')[10].string
                stat_item.rebounds=  result_item.find_all('td')[13].string
                stat_item.assists=  result_item.find_all('td')[14].string
                stat_item.points_avg=  result_item.find_all('td')[15].string
                stat_item.save_to_db()
            return {'status':'success','body':'爬蟲成功'}
        except Exception as e:
            print (e)
            return {'status':'success','body':'爬蟲失敗'}


class NBAcrawler(Resource):
    def post(self):
        try :
            rank_url = 'https://nba.hupu.com/standings'
            response = requests.get(rank_url)
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, "html.parser")
            result_east = soup.find("table",class_="players_table").find_all("tr")[2:17]
            for result_item in result_east: 
                stat_item = {}
                stat_item['rank'] =result_item.find_all('td')[0].string
                stat_item['category_id'] = 1
                stat_item['sub_category_id'] = 11
                stat_item['team_name'] = result_item.find_all('td')[1].a.string
                stat_item['win'] = result_item.find_all('td')[2].string
                stat_item['loss'] = result_item.find_all('td')[3].string
                stat_item['ranking_name'] = '東區排名'
                stat = RankModel(**stat_item)
                stat.win_rate = result_item.find_all('td')[4].string
                stat.save_to_db()
                print(result_item.find_all('td')[4])
            result_west = soup.find("table",class_="players_table").find_all("tr")[19:]
            for result_item in result_west: 
                stat_item = {}
                stat_item['rank'] =result_item.find_all('td')[0].string
                stat_item['category_id'] = 1
                stat_item['sub_category_id'] = 11
                stat_item['team_name'] = result_item.find_all('td')[1].a.string
                stat_item['win'] = result_item.find_all('td')[2].string
                stat_item['loss'] = result_item.find_all('td')[3].string
                stat_item['ranking_name'] = '西區排名'
                stat = RankModel(**stat_item)
                stat.win_rate = result_item.find_all('td')[4].string
                stat.save_to_db()
            data_url = 'https://nba.hupu.com/stats/teams'
            response = requests.get(data_url)
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("table",class_="players_table").find_all("tr")[2:]
            for result_item in result: 
                stat_item = RankModel.find_by_team(result_item.find_all('td')[1].a.string,'11')
                stat_item.field_goals_accuracy=  result_item.find_all('td')[2].string
                stat_item.three_pointers_accuracy=  result_item.find_all('td')[5].string
                stat_item.free_throws_accuracy=  result_item.find_all('td')[8].string
                stat_item.rebounds=  result_item.find_all('td')[11].string
                stat_item.assists=  result_item.find_all('td')[14].string
                stat_item.points_avg=  result_item.find_all('td')[19].string
                stat_item.save_to_db()
                return {'status':'success','body':'爬蟲成功'}
        except Exception as e:
            print (e)
            return {'status':'success','body':'爬蟲失敗'}

class Soccercrawler(Resource):
    def post(self):
        try :
            custom_headers = {
                'cache-control':'no-cache',
                'pragma':'no-cache',
                'referer':'https://live.qq.com/news/32',
            }
            delay_choices = [0.8, 0.5, 1,0.3]
            user_agent_list = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
            ]
            # 英超 18252 德甲 18291 意甲 18437 法甲 18292 亞冠17694 中超 17758 歐冠 18261 # 西甲 18326
            tabList = [
                {'tab':18252,'category':'2','subCategory':'26'},
                {'tab':18291,'category':'2','subCategory':'23'},
                {'tab':18437,'category':'2','subCategory':'22'},
                {'tab':18292,'category':'2','subCategory':'24'},
                # {'tab':17694,'category':2,'subCategory':'28'},
                {'tab':17758,'category':'2','subCategory':'25'},
                {'tab':18261,'category':'2','subCategory':'27'},
                {'tab':18326,'category':'2','subCategory':'21'},
            ]
            for tab in tabList:
                url = f"https://dongqiudi.com/sport-data/soccer/biz/data/standing?season_id={tab['tab']}&app=dqd&version=0&platform=web"
                custom_headers['User-Agent'] = random.choice(user_agent_list)
                resp = requests.get(url,headers=custom_headers)
                time.sleep(random.choice(delay_choices))
                resp.close()
                if tab['tab']== 18261 or  tab['tab']== 17758:
                    respList = json.loads(resp.text)['content']['rounds'][0]['content']['data']
                    for result_item in respList: 
                        for result in result_item['data']:
                            team = RankModel.find_by_team(result['team_name'],tab['subCategory'])
                            if team:
                                team.rank =result['rank']
                                team.win = result['matches_won']
                                team.loss = result['matches_lost']
                                team.logo = result['team_logo']
                                team.points = result['points']
                                team.save_to_db()
                            else:
                                stat_item = {}
                                stat_item['rank'] =result['rank']
                                stat_item['category_id'] = tab['category']
                                stat_item['sub_category_id'] = tab['subCategory']
                                stat_item['team_name'] = result['team_name']
                                stat_item['win'] = result['matches_won']
                                stat_item['loss'] = result['matches_lost']
                                stat_item['ranking_name'] = result_item['name']
                                stat = RankModel(**stat_item)
                                stat.logo = result['team_logo']
                                stat.points = result['points']
                                stat.save_to_db()
                else:
                    respList = json.loads(resp.text)['content']['rounds'][0]['content']['data']
                    for result_item in respList: 
                        team = RankModel.find_by_team(result_item['team_name'],tab['subCategory'])
                        if team:
                            team.rank =result_item['rank']
                            team.win = result_item['matches_won']
                            team.loss = result_item['matches_lost']
                            team.logo = result_item['team_logo']
                            team.points = result_item['points']
                            team.save_to_db()
                        else:
                            stat_item = {}
                            stat_item['rank'] =result_item['rank']
                            stat_item['category_id'] = tab['category']
                            stat_item['sub_category_id'] = tab['subCategory']
                            stat_item['team_name'] = result_item['team_name']
                            stat_item['win'] = result_item['matches_won']
                            stat_item['loss'] = result_item['matches_lost']
                            stat_item['ranking_name'] = '联赛'
                            stat = RankModel(**stat_item)
                            stat.logo = result_item['team_logo']
                            stat.points = result_item['points']
                            stat.save_to_db()
            return {'status':'success','body':'爬蟲成功'}
        except:
            traceback.print_exc()
            return {'status':'success','body':'爬蟲失敗'}

class SoccerPlayercrawler(Resource):
    def post(self):
        try :
            custom_headers = {
                'cache-control':'no-cache',
                'pragma':'no-cache',
                'referer':'https://live.qq.com/news/32',
            }
            delay_choices = [0.8, 0.5, 1,0.3]
            user_agent_list = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
            ]
            # 英超 18252 德甲 18291 意甲 18437 法甲 18292 亞冠17694 中超 17758 歐冠 18261 # 西甲 18326
            tabList = [
                {'tab':18252,'category':'2','subCategory':'26'},
                {'tab':18291,'category':'2','subCategory':'23'},
                {'tab':18437,'category':'2','subCategory':'22'},
                {'tab':18292,'category':'2','subCategory':'24'},
                {'tab':17694,'category':'2','subCategory':'28'},
                {'tab':17758,'category':'2','subCategory':'25'},
                {'tab':18261,'category':'2','subCategory':'27'},
                {'tab':18326,'category':'2','subCategory':'21'},
            ]
            StatPlayerModel.query.delete()
            for tab in tabList:
                url = f"https://dongqiudi.com/sport-data/soccer/biz/data/person_ranking?season_id={tab['tab']}&app=dqd&version=0&platform=web&type=goals"
                custom_headers['User-Agent'] = random.choice(user_agent_list)
                resp = requests.get(url,headers=custom_headers)
                time.sleep(random.choice(delay_choices))
                resp.close()
                respList = json.loads(resp.text)['content']['data']
                for result_item in respList: 
                    stat_item = {}
                    stat_item['rank'] =result_item['rank']
                    stat_item['category_id'] = tab['category']
                    stat_item['sub_category_id'] = tab['subCategory']
                    stat_item['team_name'] = result_item['team_name']
                    stat_item['player'] = result_item['person_name']
                    stat_item['player_img'] = result_item['person_logo']
                    stat_item['team_logo'] = result_item['team_logo']
                    stat_item['points'] = result_item['count']
                    stat_item['ranking_name'] = '射手榜'
                    stat = StatPlayerModel(**stat_item)
                    stat.save_to_db()
            for tab in tabList:
                url = f"https://dongqiudi.com/sport-data/soccer/biz/data/person_ranking?season_id={tab['tab']}&app=dqd&version=0&platform=web&type=assists"
                custom_headers['User-Agent'] = random.choice(user_agent_list)
                resp = requests.get(url,headers=custom_headers)
                time.sleep(random.choice(delay_choices))
                resp.close()
                respList = json.loads(resp.text)['content']['data']
                for result_item in respList: 
                    stat_item = {}
                    stat_item['rank'] =result_item['rank']
                    stat_item['category_id'] = tab['category']
                    stat_item['sub_category_id'] = tab['subCategory']
                    stat_item['team_name'] = result_item['team_name']
                    stat_item['player'] = result_item['person_name']
                    stat_item['player_img'] = result_item['person_logo']
                    stat_item['team_logo'] = result_item['team_logo']
                    stat_item['points'] = result_item['count']
                    stat_item['ranking_name'] = '助攻榜'
                    stat = StatPlayerModel(**stat_item)
                    stat.save_to_db()
            return {'status':'success','body':'爬蟲成功'}
        except:
            traceback.print_exc()
            return {'status':'success','body':'爬蟲失敗'}

class NBAPlayercrawler(Resource):
    def post(self):
        try :
            rank_url = 'https://nba.hupu.com/players'
            response = requests.get(rank_url)
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, "html.parser")
            team_list = soup.find_all("ul",class_="players_list")
            for team_item in team_list:
                for team in team_item.find_all('li'):
                    team_name = team.a.string
                    team_logo = team.img.get('src')
                    url = team.a.get('href')
                    response = requests.get(url)
                    response.encoding = 'UTF-8'
                    soup = BeautifulSoup(response.text, "html.parser")
                    player_list = soup.find("table",class_="players_table").find_all("tr")[1:]
                    for player in player_list:
                        player_name =  player.find_all("td")[1].a.string
                        player_img =  player.find("td").a.img.get('src')
                        player_url = player.find("td").a.get('href')
                        response = requests.get(player_url)
                        response.encoding = 'UTF-8'
                        soup = BeautifulSoup(response.text, "html.parser")
                        if  len(soup.find("table",class_="players_table").find_all('tr')) == 3:
                            result_list = soup.find("table",class_="players_table").find_all('tr')[2]
                            player = BasketballPlayerModel.find_by_player(player_name)
                            if player:
                                player.rebounds = result_list.find_all("td")[8].string
                                player.points_avg = result_list.find_all("td")[14].string
                                player.assists= result_list.find_all("td")[9].string
                                player.save_to_db()
                            else:
                                item = {}
                                item['category_id'] = '1'
                                item['sub_category_id'] = '11'
                                item['team_name'] = team_name 
                                item['team_logo'] = team_logo
                                item['player'] = player_name
                                item['player_img'] = player_img
                                item['rebounds'] = result_list.find_all("td")[8].string
                                item['points_avg']= result_list.find_all("td")[14].string
                                item['assists']= result_list.find_all("td")[9].string
                                new = BasketballPlayerModel(**item)
                                new.save_to_db()
            return {'status':'success','body':'爬蟲成功'}
        except:
            traceback.print_exc()
            return {'status':'success','body':'爬蟲失敗'}

class CBAPlayercrawler(Resource):
    def post(self):
        try :
            rank_url = 'http://cba.sports.sina.com.cn/cba/stats/playerstats/'
            response = requests.get(rank_url)
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, "html.parser")
            player_list = soup.find("table",id="table01").tbody.find_all('tr')
            for player in player_list:
                player_old = BasketballPlayerModel.find_by_player(player.find_all("td")[1].a.string.strip())
                print(player.find_all("td")[1].a.string.strip())
                if player_old:
                    player.rebounds = player.find_all("td")[8].string.strip()
                    player.points_avg = player.find_all("td")[4].string.strip()
                    player.assists= player.find_all("td")[11].string.strip()
                    player_old.save_to_db()
                else:
                    item = {}
                    item['category_id'] = '1'
                    item['sub_category_id'] = '12'
                    item['team_name'] = player.find_all("td")[2].string.strip()
                    item['team_logo'] = ''
                    item['player'] =  player.find_all("td")[1].a.string.strip()
                    item['player_img'] = ''
                    item['rebounds'] = player.find_all("td")[8].string.strip()
                    item['points_avg']= player.find_all("td")[4].string.strip()
                    item['assists']= player.find_all("td")[11].string.strip()
                    new = BasketballPlayerModel(**item)
                    new.save_to_db()
            return {'status':'success','body':'爬蟲成功'}
        except:
            traceback.print_exc()
            return {'status':'success','body':'爬蟲失敗'}

class GetRank(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sub_category_id',
        type = str,
        required = True,
        help = "請填寫賽事id"
    )
    def post(self):
        data = GetRank.parser.parse_args()
        list = RankModel.find_by_sub_category_id(data['sub_category_id'])
        return  {'status':'success','body':list}


class GetTeamStat(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sub_category_id',
        type = str,
        required = True,
        help = "請填寫賽事id"
    )
    parser.add_argument('type',
        type = int,
        required = True,
        help = "請填寫排行榜類型"
    )
    def post(self):
        data = GetTeamStat.parser.parse_args()
        # 得分
        list =[]
        if data['type'] == 1:
            list = RankModel.query.filter_by(sub_category_id=data['sub_category_id']).order_by(desc(cast(RankModel.points_avg,Float))).all()
        # 籃板
        elif data['type'] == 2:
            list = RankModel.query.filter_by(sub_category_id=data['sub_category_id']).order_by(desc(cast(RankModel.rebounds,Float))).all()
        # 助攻
        elif data['type'] == 3:
            list = RankModel.query.filter_by(sub_category_id=data['sub_category_id']).order_by(desc(cast(RankModel.assists,Float))).all()

        return [list_item.to_dict() for list_item in list]

class GetPlayerRank(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sub_category_id',
        type = str,
        required = True,
        help = "請填寫賽事id"
    )
    parser.add_argument('type',
        type = int,
        required = True,
        help = "請填寫排行榜類型"
    )
    # 1 射手榜 2 助攻榜
    # 1 得分榜 2 籃板榜 3 助攻榜
    def post(self):
        data = GetPlayerRank.parser.parse_args()
        if data['sub_category_id'] == '11' or data['sub_category_id'] == '12':
            if data['type'] == 1:
                list =BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.points_avg,Float)))).limit(10).all()
            elif data['type'] == 2:
                list =BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.rebounds,Float)))).limit(10).all()
            elif data['type'] == 3:
                list =BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.assists,Float)))).limit(10).all()
            else:
                rank = {}
                rank['points'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.points_avg,Float)))).limit(10).all()]
                rank['rebounds'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.rebounds,Float)))).limit(10).all()]
                rank['assists'] = [list.to_dict() for list in BasketballPlayerModel.find_by_sub_category_id(data['sub_category_id']).order_by(desc((cast(BasketballPlayerModel.assists,Float)))).limit(10).all()]
                return {'status':'success','body':rank}
        else:
            if data['type'] == 1:
                list =StatPlayerModel.find_by_sub_category_id(data['sub_category_id'],'射手榜')
            elif data['type'] == 2:
                list =StatPlayerModel.find_by_sub_category_id(data['sub_category_id'],'助攻榜')
            else:
                rank = {}
                rank['shooter'] = [list.to_dict() for list in StatPlayerModel.find_by_sub_category_id(data['sub_category_id'],'射手榜')]
                rank['assists'] = [list.to_dict() for list in StatPlayerModel.find_by_sub_category_id(data['sub_category_id'],'助攻榜')]
                return {'status':'success','body':rank}
        return  {'status':'success','body':[item.to_dict() for item in list]}

class GetHomeRank(Resource):
    def post(self):
        list = RankModel.find_by_all()
        return  {'status':'success','body':list}