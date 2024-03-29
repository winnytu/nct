from flask_restful import Resource,request,reqparse,fields,marshal
from flask_jwt_extended import jwt_required
from models.exchangeItem import ExchangeItemModel
from models.applyExchangeItem import ApplyExchangeItemModel
from itemIdGenerator import ItemIdGenerator
from sqlalchemy import desc
from sqlalchemy.sql import func

resource_fields = {
    'groupName' : fields.String,
    'album' : fields.String,   
    'category' : fields.String,
    'desc' : fields.String,
    'exchangeWay' : fields.String,
    'note' : fields.String,
    'img' : fields.String,
    'ownMember' : fields.String,
    'targetMember' : fields.String,
    'creator' : fields.String,
}

class CreateExchangeItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('groupName',type=str,required=True,help="請填寫組合名稱")
    parser.add_argument('album',type=str,required=True,help="請填寫專輯名稱")
    parser.add_argument('category',type=str,required=True,help="請填寫分類")
    parser.add_argument('desc',type=str,required=True,help="請填寫描述")
    parser.add_argument('exchangeWay',action='append',type = str,required=True,help="請填寫交易方式")
    parser.add_argument('note',type = str,action='append',required=True,help="請填寫備註")
    parser.add_argument('img',type=str,help="請上傳圖片")
    parser.add_argument('ownMember',type=str,action='append')
    parser.add_argument('targetMember',type = str,action='append',required=True,help="請填寫欲交換對象")
    parser.add_argument('creator',required=True,help="使用者名稱有誤")
    def post(self):
        data = CreateExchangeItem.parser.parse_args()
        print(data)
        itemId= ItemIdGenerator('exchange',ExchangeItemModel).create()
        item = ExchangeItemModel(itemId,**data)
        item.save_to_db()
        itemInfo = ExchangeItemModel.find_by_itemId(itemId).to_dict()
        # try: 
        #     item.save_to_db()
        # except:
        #     return {'messege': '伺服器錯誤'},500
        
        return {
            'status':'success',
            'body':itemInfo
        }      

class ModifyExchangeItem(Resource):
        parser = reqparse.RequestParser()
        parser.add_argument('itemId',type=str,required=True,help="請填寫組合名稱")
        parser.add_argument('groupName',type=str,required=True,help="請填寫組合名稱")
        parser.add_argument('album',type=str,required=True,help="請填寫專輯名稱")
        parser.add_argument('category',type=str,required=True,help="請填寫分類")
        parser.add_argument('desc',type=str,required=True,help="請填寫描述")
        parser.add_argument('exchangeWay',action='append',type = str,required=True,help="請填寫交易方式")
        parser.add_argument('note',type = str,action='append',required=True,help="請填寫備註")
        parser.add_argument('img',type=str,help="請上傳圖片")
        parser.add_argument('ownMember',type=str,action='append')
        parser.add_argument('targetMember',type = str,action='append',required=True,help="請填寫欲交換對象")
        parser.add_argument('creator',required=True,help="使用者名稱有誤")
        @jwt_required()
        def post(self):
            data = ModifyItem.parser.parse_args()
            item = ExchangeItemModel.find_by_itemId(data['itemId'])
            if item is None:
                return {'messege': '找不到該筆資料'},400
            else:
                data['id'] = item['id']
                newItem = ExchangeItemModel(**data)
                newItem.save_to_db()

            return {
                'status':'success',
                'body':ExchangeItemModel.find_by_itemId(data['itemId']).to_dict()
            }    

class ExchangeItemList(Resource):
    def post(self):
        data = request.get_json()
        curPage = data['curPage']
        # if (data['creator']):
        #     return {'items':[item.json() for item in ExchangeItemModel.find_by_creator(data['creator'])]}
        if data['sortType'] == 'hot':
            itemList = []
            for item in ExchangeItemModel.query.outerjoin(ApplyExchangeItemModel).group_by(ExchangeItemModel.id).order_by(func.count(ApplyExchangeItemModel.id).desc(), ExchangeItemModel.create_time.desc()).limit(12).offset((curPage*10)-10).all():
                newItem = item.to_dict()
                newItem['applyCount'] = item.relatedApplyItems.count()
                itemList.append(newItem)
            return {'status':'success','body':itemList,'totalCount':ExchangeItemModel.query.count()}
        else:
            itemList = []
            for item in ExchangeItemModel.query.order_by(desc('create_time')).limit(12).offset((curPage*10)-10).all():
                newItem = item.to_dict()
                newItem['applyCount'] = item.relatedApplyItems.count()
                itemList.append(newItem)
            return {'status':'success','body':itemList,'totalCount':ExchangeItemModel.query.count()}

class GetExchangeApplyList(Resource):
    def post(self):
        data = request.get_json()
        if (data['itemId']):
            return {'messageList':ExchangeItemModel.find_related_apply_items(data['itemId'])}


class ExchangeMessageList(Resource):
    def post(self):
        data = request.get_json()
        return {'messageList':ExchangeItemModel.find_apply_messages(data['itemId'],data['applier'],data['creator'])}

    
