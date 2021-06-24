from flask_restful import Resource,request,reqparse,fields,marshal
from flask_jwt_extended import jwt_required
from models.applyExchangeItem import ApplyExchangeItemModel
from models.message import MessageModel

class ApplyExchangeItem(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('itemId',type=str,required=True,help="請填寫組合名稱")
    parser.add_argument('exchangeWay',type=str,action='append',required=True,help="請填寫專輯名稱")
    parser.add_argument('ownMember',type=str,action='append',required=True,help="請填寫分類")
    parser.add_argument('targetMember',type=str,action='append',required=True,help="請填寫描述")
    parser.add_argument('applier',type=str,required=True,help="請填寫描述")
    @jwt_required()
    def post(self):
        data = ApplyExchangeItem.parser.parse_args()
        item = ApplyExchangeItemModel(**data)
        print(request.get_json())
        message =  request.get_json()['message']
        print(message)
        postMassage = MessageModel('unread',**message)
        item.save_to_db()
        postMassage.save_to_db()
        # try: 
        #     item.save_to_db()
        #     postMassage.save_to_db()
        # except:
        #     return {'messege': '伺服器錯誤'},500
        return {'message':'已送出申請'}
        

        

