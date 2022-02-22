#coding:utf-8
import os
import re
from flask import Flask,make_response
from flask_restful import Api
# resource creating some data
from flask_jwt_extended import JWTManager
#from flask_migrate import Migrate
from resources.category import GetCategory,UpdateMainCategory,UpdateSubCategory,UpdateStatus,UpdateSort
from resources.user import ResetPassword, UserRegister,UserPhoneLogin,UserPasswordLogin,ResetPassword,UserUpdate,TokenRefresh,SendVerification,GetUserInfo,GetUserList,GetUserDetail,ToggleUserStatus,ToggleUserChatStatus,ToggleUserPublishStatus,UserAvatar
from resources.match import MatchCrawler,GetMatchEventSchedule,GetMatchRoomList,GetMatchLive,GetMatchTab,GetMatchStat,GetTeamAnalyze,GetTeamHistory,GetHomeHistory,GetAwayHistory,GetWinStat,GetResultStat
from resources.article import ArticleCrawler,GetArticleTab,GetArticleList,GetAllArticleList,GetArticleDetail,GetHotArticleList,ToggleArticleReplyStatus,ToggleArticleShowStatus,EditArticle,DeleteArticle,SearchArticle
from resources.live import GetLiveList, GetLiveTab
from resources.comment import GetCommentList,AddComment
from resources.like import LikeArticle,LikeComment
from resources.banner import GetBannerList,UpdateBanner,ToggleBannerStatus
from resources.home import HomeInfo,HomeLive
from resources.event import UpdateEvent,ToggleEventStatus,GetEventAllList,GetEventShowList,GetEventDetail,DeleteEvent
from resources.notification import CreateNotification,GetAllNotification,GetNotificationList,GetNotificationCount,ReadNotification,HideNotification,HideAllNotification,EditNotification
from resources.stat import CBAcrawler,NBAcrawler,GetRank,GetTeamStat,Soccercrawler,SoccerPlayercrawler,GetPlayerRank,NBAPlayercrawler,CBAPlayercrawler,GetHomeRank
from db import db
from flask_cors import CORS
import datetime
from config.config import SysConfig

app = Flask(__name__)
CORS(app, supports_credentials=True)

#load config depend on env
conf_file = f'{app.root_path}/config/config.cfg'
result = SysConfig(conf_file, os.environ.get('FLASK_ENV', 'heroku'))
app.config.update(result.get())

#DATABASE_URL is heroku variable of env, string like 'postgres://'
if os.environ.get('FLASK_ENV') == "heroku":
    uri = os.environ.get("DATABASE_URL",'postgresql://postgres:0815@localhost/sport168')   # or other relevant config var
    uri = re.sub("^postgres://", "postgresql://", uri, 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

db.init_app(app)
api = Api(app)
#Migrate(app,db)

# create table
@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_payload, jwt_headers):
    return {
        'message': '憑證過期',
        'errCode': '80000'
    }, 401


api.add_resource(SendVerification,'/user/sendVerification')
api.add_resource(UserPhoneLogin,'/user/phoneLogin')
api.add_resource(UserPasswordLogin,'/user/passwordLogin')
api.add_resource(UserRegister,'/user/register')
api.add_resource(ResetPassword,'/user/reset')
api.add_resource(UserUpdate,'/user/update')
api.add_resource(TokenRefresh,'/user/refresh')
api.add_resource(GetUserInfo,'/user/info')
api.add_resource(GetUserList,'/user/list')
api.add_resource(GetUserDetail,'/user/detail')
api.add_resource(ToggleUserStatus,'/user/toggleStatus')
api.add_resource(ToggleUserChatStatus,'/user/toggleChatStatus')
api.add_resource(ToggleUserPublishStatus,'/user/togglePublishStatus')
api.add_resource(UserAvatar,'/user/avatar')


api.add_resource(GetCategory,'/category/list')
api.add_resource(UpdateMainCategory,'/category/updateMain')
api.add_resource(UpdateSubCategory,'/category/updateSub')
api.add_resource(UpdateStatus,'/category/status')
api.add_resource(UpdateSort,'/category/sort')

api.add_resource(GetMatchEventSchedule,'/match/schedule')
api.add_resource(GetMatchRoomList,'/match/room')
api.add_resource(GetMatchLive,'/match/live')
api.add_resource(MatchCrawler,'/match/crawler')
api.add_resource(GetMatchTab,'/match/tab')

api.add_resource(GetMatchStat,'/match/stat')
api.add_resource(GetTeamAnalyze,'/match/teamAnalyze')
api.add_resource(GetTeamHistory,'/match/teamHistory')
api.add_resource(GetHomeHistory,'/match/homeHistory')
api.add_resource(GetAwayHistory,'/match/awayHistory')
api.add_resource(GetWinStat,'/match/winStat')
api.add_resource(GetResultStat,'/match/resultStat')

api.add_resource(ArticleCrawler,'/article/crawler')
api.add_resource(GetArticleTab,'/article/tab')
api.add_resource(GetArticleList,'/article/list')
api.add_resource(GetAllArticleList,'/article/allList')
api.add_resource(GetArticleDetail,'/article/detail')
api.add_resource(GetHotArticleList,'/article/hot')
api.add_resource(ToggleArticleShowStatus,'/article/toggleShowStatus')
api.add_resource(ToggleArticleReplyStatus,'/article/toggleReplyStatus')
api.add_resource(EditArticle,'/article/edit')
api.add_resource(DeleteArticle,'/article/delete')
api.add_resource(SearchArticle,'/search')

api.add_resource(GetCommentList,'/comment/list')
api.add_resource(AddComment,'/comment/add')

api.add_resource(LikeComment,'/like/comment')
api.add_resource(LikeArticle,'/like/article')

api.add_resource(GetLiveTab,'/live/tab')
api.add_resource(GetLiveList,'/live/list')

api.add_resource(GetBannerList,'/banner/list')
api.add_resource(UpdateBanner,'/banner/update')
api.add_resource(ToggleBannerStatus,'/banner/status')

api.add_resource(HomeInfo,'/home/info')
api.add_resource(HomeLive,'/home/live')

api.add_resource(UpdateEvent,'/event/update')
api.add_resource(GetEventAllList,'/event/allList')
api.add_resource(GetEventShowList,'/event/list')
api.add_resource(GetEventDetail,'/event/detail')
api.add_resource(ToggleEventStatus,'/event/status')
api.add_resource(DeleteEvent,'/event/delete')

api.add_resource(CreateNotification,'/notification/create')
api.add_resource(GetAllNotification,'/notification/all')
api.add_resource(GetNotificationList,'/notification/list')
api.add_resource(GetNotificationCount,'/notification/count')
api.add_resource(ReadNotification,'/notification/read')
api.add_resource(HideNotification,'/notification/delete')
api.add_resource(HideAllNotification,'/notification/hide')
api.add_resource(EditNotification,'/notification/edit')

api.add_resource(CBAcrawler,'/stat/cba')
api.add_resource(NBAcrawler,'/stat/nba')
api.add_resource(GetRank,'/stat/rank')
api.add_resource(GetTeamStat,'/stat/teamStat')
api.add_resource(Soccercrawler,'/stat/soccer')
api.add_resource(SoccerPlayercrawler,'/stat/soccerPlayer')
api.add_resource(GetPlayerRank,'/stat/player')
api.add_resource(NBAPlayercrawler,'/stat/nbaPlayer')
api.add_resource(CBAPlayercrawler,'/stat/CBAPlayer')
api.add_resource(GetHomeRank,'/stat/homeRank')
# 只要在run這個檔案的時候才會執行 沒加的話則是import的時候就會執行
if __name__ == "__main__":
    app.run(port=5000)
