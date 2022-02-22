from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.event import EventModel
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import requests
import json
import time
from datetime import datetime, timedelta,date
from bs4 import BeautifulSoup
from imageSave import ImageSave

class GetEventAllList(Resource):
    def post(self):
            today = datetime.now()
            print(today)
            event_list =  [event.to_dict() for event in EventModel.query.order_by('start_date').all()]
            total = EventModel.query.count()
            now_count = EventModel.query.filter(EventModel.end_date>today).filter(EventModel.start_date<today).order_by('start_date').count()
            end_count =  EventModel.query.filter(EventModel.end_date<today).order_by('start_date').count()
            return {'status':'success','body':{'eventList':event_list,'total':total,'now':now_count,'end':end_count}}

class GetEventShowList(Resource):
    def post(self):
            event_list =  [event.to_dict() for event in EventModel.find_by_start()]
            end_event_list =  [event.to_dict() for event in EventModel.find_by_end()]
            return {'status':'success','body': {'startList':event_list,'endList':end_event_list}}

class GetEventDetail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
        type = str,
        required = True,
        help = "請填寫id"
    )
    def post(self):
        data = GetEventDetail.parser.parse_args()
        event =  EventModel.find_by_id(data['id']).to_dict()
        return {'status':'success','body':event}

class UpdateEvent(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id',
        type = str,
        required = False,
    )
    parser.add_argument('event_id',
        type = str,
        required = True,
        help = "請填寫活動id"
    )
    parser.add_argument('title',
        type = str,
        required = True,
        help = "請填寫活動標題"
    )
    parser.add_argument('sub_title',
        type = str,
        required = True,
        help = "請填寫活動副標題"
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
    parser.add_argument('remark',
        type = str,
        required = False,
    )
    parser.add_argument('content',
        type = str,
        required = False,
    )
    def post(self):
        data = UpdateEvent.parser.parse_args()
        if data['id'] and EventModel.find_by_id(data['id']):
            event = EventModel.find_by_id(data['id'])
            event.title = data['title']
            event.sub_title = data['sub_title']
            event.url = data['url']
            event.url_type = data['url_type']
            event.event_id = data['event_id']
            event.start_date = data['start_date']
            event.end_date = data['end_date']
            event.img = data['img']
            event.remark = data['remark']
            event.content = data['content']
            img = ImageSave(event.id,data['img'],'event').ImageSave()
            event.img = img
            event.save_to_db()
            return {'status':'success','body': event.to_dict()}
        else:
            del data['id']
            new_event = EventModel(**data)
            new_event.save_to_db()
            img = ImageSave(new_event.id,data['img'],'event').ImageSave()
            new_event.img = img
            new_event.save_to_db()
            return {'status':'success','body': new_event.to_dict()}

class ToggleEventStatus(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('idList',
        type = str,
        required = True,
        action='append',
        help = "請填寫id"
    )
    parser.add_argument('status',
        type = str,
        required = True,
        help = "請填寫狀態"
    )
    def post(self):
        data = ToggleEventStatus.parser.parse_args()
        for id in data['idList']:
            banner = EventModel.find_by_id(id)
            banner.show_status = data['status']
            banner.save_to_db()
        return {'status':'success','body': '狀態更新成功'}

class DeleteEvent(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('idList',
        type = str,
        action='append',
        required = True,
        help = "請填寫id"
    )
    def post(self):
        data = DeleteEvent.parser.parse_args()
        for id in data['idList']:
            event = EventModel.find_by_id(id)
            event.delete_from_db()
        return {'status':'success','body':'刪除成功'}
