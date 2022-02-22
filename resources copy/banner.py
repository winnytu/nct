from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.banner import BannerModel
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
from bs4 import BeautifulSoup
from imageSave import ImageSave

class GetBannerList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('position',
        type = str,
        action='append',
        required = False,
        help = "請填寫位置"
    )
    parser.add_argument('device',
        type = str,
        required = True,
        help = "請填寫裝置"
    )
    def post(self):
        data =GetBannerList.parser.parse_args()
        if data['position']:
            banner_list =  BannerModel.find_by_position(data['position'],data['device'])
            return {'status':'success','body':banner_list}
        else:
            banner_list =  BannerModel.find_by_device(data['device'])
            print(1)
            return {'status':'success','body': banner_list}
        
        

class UpdateBanner(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
        type = str,
        required = False,
    )
    parser.add_argument('position',
        type = str,
        required = True,
        help = "請填寫廣告位置"
    )
    parser.add_argument('order',
        type = str,
        required = True,
        help = "請填寫順序"
    )
    parser.add_argument('title',
        type = str,
        required = True,
        help = "請填寫標題"
    )
    parser.add_argument('url',
        type = str,
        required = True,
        help = "請填寫連結"
    )
    parser.add_argument('url_type',
        type = str,
        required = True,
        help = "請填寫連結類型"
    )
    parser.add_argument('start_date',
        type = str,
        required = True,
        help = "請填寫開始日期"
    )
    parser.add_argument('end_date',
        type = str,
        required = True,
        help = "請填寫結束日期"
    )
    parser.add_argument('img',
        type = str,
        required = True,
        help = "請填寫圖片"
    )
    parser.add_argument('text',
        type = str,
        required = True,
        help = "請填寫文字"
    )
    parser.add_argument('video_url',
        type = str,
        required = True,
        help = "請填寫影片網址"
    )
    parser.add_argument('device',
        type = str,
        required = True,
        help = "請填寫裝置"
    )
    def post(self):
        data = UpdateBanner.parser.parse_args()
        if data['id'] and BannerModel.find_by_id(data['id']):
            banner = BannerModel.find_by_id(data['id'])
            banner.title = data['title']
            banner.position = data['position']
            banner.order = data['order']
            banner.start_date = data['start_date']
            banner.end_date = data['end_date']
            banner.url = data['url']
            banner.url_type = data['url_type']
            img = ImageSave(data['id'],data['img'],'banner').ImageSave()
            banner.img = img
            banner.text = data['text']
            banner.video_url = data['video_url']
            banner.device = data['device']
            banner.save_to_db()
            return {'status':'success','body': banner.to_dict()}
        else:
            banner = BannerModel(data['position'],data['order'],data['title'])
            banner.save_to_db()
            print(banner.id)
            img = ImageSave(banner.id,data['img'],'banner').ImageSave()
            banner.start_date = data['start_date']
            banner.end_date = data['end_date']
            banner.url = data['url']
            banner.url_type = data['url_type']
            banner.img = img
            banner.text = data['text']
            banner.video_url = data['video_url']
            banner.device = data['device']
            banner.save_to_db()
            return {'status':'success','body': banner.to_dict()}

class ToggleBannerStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
        type = str,
        required = True,
        help = "請填寫id"
    )
    parser.add_argument('status',
        type = str,
        required = True,
        help = "請填寫狀態"
    )
    def post(self):
        data = ToggleBannerStatus.parser.parse_args()
        banner = BannerModel.find_by_id(data['id'])
        banner.show_status = data['status']
        banner.save_to_db()
        return {'status':'success','body': '狀態更新成功'}

