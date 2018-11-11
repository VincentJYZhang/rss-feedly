from flask import jsonify, request, session
from .__init__ import api
from app.models.model import User
from .tools import apiTools
from db import db
import re


@api.route('/user/info/', methods=['GET'])
def getInfo():
    response_json = {"code" : "1"}
    if 'user_id' not in session:
        response_json['code'] = "0"
    else:
        # 数据库查询
        user = User.query.filter(User.id == session["user_id"]).first()
        response_json['code'] = "1"
        response_json['nick'] = user.nickname
        response_json['mail'] = user.email
        response_json['confirm'] = user.vertification

    return jsonify(response_json)

@api.route('/user/logout', methods = ["GET"])
def logout():

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    session.pop("user_id")
    session.pop("user_name")
    session.pop("user_mail")

    return jsonify({"code": "1"})


@api.route('/user/confirm', methods = ["GET"])
def confirm():

    response_json = {}

    mail = request.headers["user_mail"]
    pwd = request.headers["user_pwd"]

    user = User.query.filter(User.email == mail, User.password == pwd).first()

    if user is None:
        response_json["code"] = "0"
    else:
        response_json["code"] = "1"
        response_json["confirm"] = user.vertification
        session["user_id"] = user.id
        session["user_name"] = user.nickname
        session["user_mail"] = user.email

    return jsonify(response_json)


@api.route('/user/register', methods=["POST"])
def register():

    if re.match(r'[^@]+@[^@]+\.[^@]+', request.headers['user_mail']) is None:
        return jsonify({"code": "-2"})

    user = User.query.filter(User.email == request.headers["user_mail"]).first()
    if user is not None:
        return jsonify({"code": "-1"})

    user = User()
    user.email = request.headers['user_mail']
    user.password = request.headers['user_pwd']
    user.nickname = request.headers['user_nickname']
    db.session.add(user)
    db.session.commit()

    return jsonify({"code": "1"})

@api.route('/user/modify', methods=["POST"])
def modify():

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    user = User.query.filter(User.id == session["user_id"]).first()

    if user is None:
        return jsonify({"code": "-2"})

    if "user_nickname" in request.headers:
        user.nickname = request.headers["user_nickname"]
        session["user_name"] = request.headers["user_nickname"]
        db.session.commit()

    if "user_pwd" in request.headers:
        user.password = request.headers["user_pwd"]
        session.pop("user_id")
        session.pop("user_name")
        session.pop("user_mail")
        db.session.commit()

    return jsonify({"code": "1"})