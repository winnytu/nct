from flask_restful import Resource,request,reqparse,fields,marshal
from flask_jwt_extended import jwt_required
from models.togetherItem import TogetherItemModel
from models.applyTogetherItem import ApplyTogetherItemModel
from itemIdGenerator import ItemIdGenerator
from sqlalchemy import desc
from sqlalchemy.sql import func

resource_fields = {
    'itemTitle' : fields.String, 
    'groupName' : fields.String,
    'category' : fields.String,
    'desc' : fields.String,
    'img' : fields.String,
    'itemList' : fields.String,
    'creator' : fields.String,
    'expired_time' : fields.String,
}
class CreateTogetherItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('itemTitle',type=str,required=True,help="請填寫專輯名稱")
    parser.add_argument('groupName',type=str,required=True,help="請填寫組合名稱")
    parser.add_argument('category',type=str,required=True,help="請填寫分類")
    parser.add_argument('desc',type=str,required=True,help="請填寫描述")
    parser.add_argument('rule',type=str,required=True,help="請填寫描述")
    parser.add_argument('img',type=str,help="請上傳圖片")
    parser.add_argument('itemListA',type=list,action='append')
    parser.add_argument('itemListB',type=list,action='append')
    parser.add_argument('expired_time',type =str,required=True,help="請填寫欲交換對象")
    parser.add_argument('creator',required=True,help="使用者名稱有誤")
    def post(self):
        data = CreateTogetherItem.parser.parse_args()
        itemId= ItemIdGenerator('together',TogetherItemModel).create()
        item = TogetherItemModel(itemId,**data)
        item.save_to_db()
        itemInfo = TogetherItemModel.find_by_itemId(itemId).to_dict()
        # try: 
        #     item.save_to_db()
        # except:
        #     return {'messege': '伺服器錯誤'},500
        return {
            'status':'success',
            'body':itemInfo
        }      

class ModifyItem(Resource):
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
            item = TogetherItemModel.find_by_itemId(data['itemId'])
            if item is None:
                return {'messege': '找不到該筆資料'},400
            else:
                data['id'] = item['id']
                newItem = TogetherItemModel(**data)
                newItem.save_to_db()

            return {
                'status':'success',
                'body':TogetherItemModel.find_by_itemId(data['itemId']).to_dict()
            }    

class TogetherItemList(Resource):
    def post(self):
        data = request.get_json()
        curPage = data['curPage']
        # if (data['creator']):
        #     return {'items':[item.json() for item in TogetherItemModel.find_by_creator(data['creator'])]}
        if data['sortType'] == 'hot':
            itemList = []
            for item in TogetherItemModel.query.outerjoin(ApplyTogetherItemModel).group_by(TogetherItemModel.id).order_by(func.count(ApplyTogetherItemModel.id).desc(), TogetherItemModel.create_time.desc()).limit(12).offset((curPage*10)-10).all():
                newItem = item.to_dict()
                newItem['applyCount'] = item.relatedApplyItems.count()
                itemList.append(newItem)
            return {'status':'success','body':itemList,'totalCount':TogetherItemModel.query.count()}
        else:
            itemList = []
            for item in TogetherItemModel.query.order_by(desc('create_time')).limit(12).offset((curPage*10)-10).all():
                newItem = item.to_dict()
                newItem['applyCount'] = item.relatedApplyItems.count()
                itemList.append(newItem)
            return {'status':'success','body':itemList,'totalCount':TogetherItemModel.query.count()}

class GetTogetherApplyList(Resource):
    def post(self):
        data = request.get_json()
        if (data['itemId']):
            return {'messageList':TogetherItemModel.find_related_apply_items(data['itemId'])}


class TogetherMessageList(Resource):
    def post(self):
        data = request.get_json()
        return {'messageList':TogetherItemModel.find_apply_messages(data['itemId'],data['applier'],data['creator'])}

    
