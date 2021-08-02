from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.togetherMessage import TogetherMessageModel
from models.exchangeMessage import ExchangeMessageModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity
)
import json
class SendExchangeMessage(Resource):
    def post(self):
        message = request.get_json()
        postMassage = ExchangeMessageModel('unread',**message)
        postMassage.save_to_db()
        return {
            'status':'success',
            'body':message
        }, 200

class SendTogetherMessage(Resource):
    def post(self):
        message = request.get_json()
        postMassage = TogetherMessageModel('unread',**message)
        postMassage.save_to_db()
        return {
            'status':'success',
            'body':message
        }, 200