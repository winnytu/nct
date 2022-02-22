from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.category import MainCategoryModel,SubCategoryModel
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
import ast
from bs4 import BeautifulSoup
from sqlalchemy import asc
from imageSave import ImageSave

class GetCategory(Resource):
    def post(self):
        newsCategory = MainCategoryModel.find_all()
        list = []
        for category in newsCategory:
            new = category.to_dict()
            new['sub_list'] = MainCategoryModel.find_sub_category_list(new['category_id'])
            list.append(new)
        return {'status':'success','body': list}

class UpdateMainCategory(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category',
        type = str,
        required = True,
        help = "請填寫分類名稱"
    )
    parser.add_argument('category_id',
        type = str,
        required = True,
        help = "請填寫分類id"
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫更新類型"
    )
    parser.add_argument('icon',
        type = str,
        required = True,
        help = "請填寫圖示"
    )
    def post(self):
        data = UpdateMainCategory.parser.parse_args()
        type = data['type']
        category = MainCategoryModel.find_by_category(data['category_id'])
        if type == 'add':
            if category:
                return {'err':'81001','errMsg':'該分類編碼已存在','body':category.to_dict()}
            else:
                new = MainCategoryModel(data['category'],data['category_id'])
                icon = ImageSave(data['category_id'],data['icon'],'category').ImageSave()
                new.icon = icon
                new.save_to_db()
                newsCategory = MainCategoryModel.find_all()
                list = []
                for category in newsCategory:
                    new = category.to_dict()
                    new['sub_list'] = MainCategoryModel.find_sub_category_list(new['category_id'])
                    list.append(new)
                return {'status':'success','body': list}
        if type == 'update':
            category.category = data['category']
            icon = ImageSave(data['category_id'],data['icon'],'category').ImageSave()
            category.icon = icon
            category.save_to_db()
            newsCategory = MainCategoryModel.find_all()
            list = []
            for category in newsCategory:
                new = category.to_dict()
                new['sub_list'] = MainCategoryModel.find_sub_category_list(new['category_id'])
                list.append(new)
            return {'status':'success','body': list}

class UpdateSubCategory(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category_id',
        type = str,
        required = True,
        help = "請填寫分類id"
    )
    parser.add_argument('sub_category',
        type = str,
        required = True,
        help = "請填寫子分類"
    )
    parser.add_argument('sub_category_id',
        type = str,
        required = True,
        help = "請填寫子分類id"
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫更新類型"
    )
    parser.add_argument('icon',
        type = str,
        required = True,
        help = "請填寫圖示"
    )
    def post(self):
        data = UpdateSubCategory.parser.parse_args()
        category = SubCategoryModel.find_by_sub_category(data['sub_category_id'])
        type = data['type']
        if type == 'add':
            if category:
                return {'err':'81001','errMsg':'該分類編碼已存在','body':category.to_dict()}
            else:
                new = SubCategoryModel(data['category_id'],data['sub_category'],data['sub_category_id'])
                icon = ImageSave(data['sub_category_id'],data['icon'],'sub-category').ImageSave()
                new.icon = icon
                new.save_to_db()
                newsCategory = SubCategoryModel.find_all()
                list = []
                for category in newsCategory:
                    new = category.to_dict()
                    new['sub_list'] = MainCategoryModel.find_sub_category_list(new['category_id'])
                    list.append(new)
                return {'status':'success','body': list}
        if type == 'update':
            category.sub_category = data['sub_category']
            icon = ImageSave(data['sub_category_id'],data['icon'],'sub-category').ImageSave()
            category.icon = icon
            category.save_to_db()
            newsCategory = MainCategoryModel.find_all()
            list = []
            for category in newsCategory:
                new = category.to_dict()
                new['sub_list'] = MainCategoryModel.find_sub_category_list(new['category_id'])
                list.append(new)
            return {'status':'success','body': list}

class UpdateStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('list',
        type = str,
        action='append',
        required = True,
        help = "請填寫子分類id"
    )
    parser.add_argument('mainList',
        type = str,
        action='append',
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫類型"
    )
    def post(self):
        data = UpdateStatus.parser.parse_args()
        sub_list = SubCategoryModel.find_all()
        for sub in sub_list:
            if sub.sub_category_id in data['list']:
                if data['type'] == 'article':
                    sub.article_status = 1
                elif data['type'] == 'match':
                    sub.match_status = 1
                elif data['type'] == 'live':
                    sub.live_status = 1
                elif data['type'] == 'video':
                    sub.video_status = 1
            else:
                if data['type'] == 'article':
                    sub.article_status = 0
                elif data['type'] == 'match':
                    sub.match_status = 0
                elif data['type'] == 'live':
                    sub.live_status = 0
                elif data['type'] == 'video':
                    sub.video_status = 0
            sub.save_to_db()
        if data.get('mainList'):
            main_list = MainCategoryModel.find_all()
            for main in main_list:
                if main.category_id in data.get('mainList'):
                    main.match_status = 1
                else:
                    main.match_status = 0
            main.save_to_db()
        if data['type'] == 'article':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.article_status!=0).order_by(asc('article_status')).all()]
        elif data['type'] == 'match':
            mainTab = MainCategoryModel.query.filter(MainCategoryModel.match_status!=0).order_by(asc('match_status')).all()
            tabList = []
            for main in mainTab:
                mainList = main.to_dict()
                mainList['subTabList'] = [tab.to_dict() for tab in SubCategoryModel.query.filter_by(category_id=main.category_id).filter(SubCategoryModel.match_status!=0).order_by(asc('match_status')).all()]
                tabList.append(mainList)
        elif data['type'] == 'live':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.live_status!=0).order_by(asc('live_status')).all()]
        elif data['type'] == 'video':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.video_status!=0).order_by(asc('video_status')).all()]
        
        return {'status':'success','body': tabList}


class UpdateSort(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('list',
        action='append',
        required = True,
        help = "請填寫子分類id"
    )
    parser.add_argument('type',
        type = str,
        required = True,
        help = "請填寫類型"
    )
    def post(self):
        data = UpdateStatus.parser.parse_args()
        list = data['list']
        if data['type'] == 'match':
            for item_str in list:
                item = ast.literal_eval(item_str)
                category = MainCategoryModel.find_by_category(item['category_id'])
                category.match_status = item['sort']
                category.save_to_db()
                for sub in item['subTabList']:
                    sub_category = SubCategoryModel.find_by_sub_category(sub['sub_category_id'])
                    sub_category.match_status = sub['sort']
                    sub_category.save_to_db()
        else:
            for item_str in list:
                item = ast.literal_eval(item_str)
                category = SubCategoryModel.find_by_sub_category(item['sub_category_id'])
                if data['type'] == 'article':
                    category.article_status = item['sort']
                elif data['type'] == 'live':
                    category.live_status = item['sort']
                elif data['type'] == 'video':
                    category.video_status = item['sort']
                category.save_to_db()
        if data['type'] == 'article':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.article_status!=0).order_by(asc('article_status')).all()]
        elif data['type'] == 'match':
            mainTab = MainCategoryModel.query.filter(MainCategoryModel.match_status!=0).order_by(asc('match_status')).all()
            tabList = []
            for main in mainTab:
                mainList = main.to_dict()
                mainList['subTabList'] = [tab.to_dict() for tab in SubCategoryModel.query.filter_by(category_id=main.category_id).filter(SubCategoryModel.match_status!=0).order_by(asc('match_status')).all()]
                tabList.append(mainList)
        elif data['type'] == 'live':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.live_status!=0).order_by(asc('live_status')).all()]
        elif data['type'] == 'video':
            tabList = [tab.to_dict() for tab in SubCategoryModel.query.filter(SubCategoryModel.video_status!=0).order_by(asc('video_status')).all()]
        
        return {'status':'success','body': tabList}