from flask import jsonify
from flask_restful import Resource,reqparse,request,fields,marshal
from models.like import LikeModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,create_refresh_token,
    get_jwt_identity,jwt_required
)
import json

class LikeComment(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userId',
        type = str,
        required = True,
        help = "請填寫會員uid"
    )
    parser.add_argument('commentId',
        type = str,
        required = True,
        help = "請填寫評論id"
    )
    @jwt_required()
    def post(self):
        data = LikeComment.parser.parse_args()
        like = LikeModel(data['userId'])
        like.save_to_db()
        like.comment_id = data['commentId']
        like.save_to_db()
        return {
            'status':'success',
            'body':'按讚成功'
        }, 200

class LikeArticle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userId',
        type = str,
        required = True,
        help = "請填寫會員uid"
    )
    parser.add_argument('articleId',
        type = str,
        required = True,
        help = "請填寫新聞id"
    )
    @jwt_required()
    def post(self):
        data = LikeArticle.parser.parse_args()
        like = LikeModel(data['userId'])
        like.save_to_db()
        like.article_id = data['articleId']
        like.save_to_db()
        return {
            'status':'success',
            'body':'按讚成功'
        }, 200
# class likeArticle(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument('articleId',
#         type = str,
#         required = True,
#         help = "請填寫id"
#     )
#     def post(self):
#         data = likeArticle.parser.parse_args()
#         article = ArticleModel.find_by_id(data['articleId'])
#         like_num = article.like 
#         article.like = like_num + 1
#         article.save_to_db()
#         return {'status':'success','body': article.to_dict()}