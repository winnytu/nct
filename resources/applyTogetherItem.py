from flask_restful import Resource,request,reqparse,fields,marshal
from flask_jwt_extended import jwt_required
from models.applyTogetherItem import ApplyTogetherItemModel
from models.togetherMessage import TogetherMessageModel
from models.togetherItem import TogetherItemModel
from models.notification import NotificationModel
import json

class ApplyTogetherItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('itemId',type=str,required=True,help="請填寫組合名稱")
    parser.add_argument('itemListA',type=list,action='append',help="請填寫分類")
    parser.add_argument('itemListB',type=list,action='append',help="請填寫分類")
    parser.add_argument('applier',type=str,required=True,help="請填寫描述")
    @jwt_required()
    def post(self):
        data = ApplyTogetherItem.parser.parse_args()
        item = ApplyTogetherItemModel(**data)
        message =  request.get_json()['message']
        postMassage = TogetherMessageModel('unread',**message)
        originItem= TogetherItemModel.find_by_itemId(data['itemId'])
        newItemListA = []
        newItemListB = []
        if  originItem.rule == 'A' or originItem.rule == 'C':
            for i in originItem.itemListA:
                for j in data['itemListA']:
                    if (i[0] == j[0]):
                        i[1] = str(int(i[1])-int(j[1])) 
                        newItemListA.append(i)
            for i in originItem.itemListB:
                for j in data['itemListB']:
                    if (i[0] == j[0]):
                        i[1] = str(int(i[1])-int(j[1])) 
                        newItemListB.append(i)
        item.save_to_db()
        postMassage.save_to_db()
        originItem.itemListA = newItemListA
        originItem.itemListB = newItemListB
        originItem.update_to_db()
        newNotification = NotificationModel('unread','訂單','您有一筆新團申請','您的『'+originItem.itemTitle+'』有一筆新申請',originItem.creator)
        newNotification.save_to_db()
        return {'status':'success','message':'已送出申請'}
        

class CheckApplyStatus(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        item = ApplyTogetherItemModel.find_by_itemId_userName(data['itemId'],data['userName'])
        if item is None:
            return {'applyStatus':0,'message':'未送出申請'}
        return {'applyStatus':1,'message':'已送出申請'}
        

