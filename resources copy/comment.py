from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.comment import CommentModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import json
from idGenerator import IdWorker
import random, string
class GetCommentList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('articleId',
        type = str,
        required = True,
        help = "請填寫新聞id"
    )
    parser.add_argument('userId',
        type = str,
        required = False,
        help = "請填寫新聞id"
    )
    def post(self):
        data = GetCommentList.parser.parse_args()
        commentList = CommentModel.find_by_article(data['articleId'],data['userId'])
        return {
            'status':'success',
            'body':commentList
        }, 200

class AddComment(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('articleId',
        type = str,
        required = True,
        help = "請填寫新聞id"
    )
    parser.add_argument('userId',
        type = str,
        required = True,
        help = "請填寫用戶id"
    )
    parser.add_argument('commentId',
        type = str,
        required = False,
    )
    parser.add_argument('comment',
        type = str,
        required = True,
        help = "請填寫留言"
    )
    @jwt_required()
    def post(self):
        data = AddComment.parser.parse_args()
        comment = CommentModel(data['articleId'],data['userId'],data['comment'])
        comment.save_to_db()
        comment.comment_id = ''.join(random.choice(string.ascii_letters) for x in range(10)) + str(IdWorker(1,1,comment.id))
        comment.save_to_db()
        if data['commentId']:
            comment.reply_id = data['commentId']
            comment.save_to_db()
        return {
            'status':'success',
            'body':comment.to_dict()
        }, 200

class LikeComment(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        notification = NotificationModel.find_by_id(data['id'])
        notification.status = 'read'
        notification.save_to_db()
        return {
            'status':'success',
        }, 200