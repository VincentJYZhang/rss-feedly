from flask import jsonify, request, session
from .__init__ import api
from db import db
from datetime import datetime
from .tools import apiTools
from app.models.model import Feed, Subscribe, Item, ReadLog
from app.api.config import item_update_limit, feed_getItem_limit


@api.route('/item/<item_id>', methods = ['GET'])
def getItem(item_id):

    item = Item.query.filter(Item.id == item_id).first()

    if item is None:
        return jsonify({"code": "-1"})

    rlog = ReadLog.query.filter(ReadLog.item_id == item.id).first()

    response_json = {"id": item.id, "url": item.url,
                 "author": item.author, "guide": item.guide, "title": item.title,
                 "content": item.content, "pub_time": item.pub_time}

    if rlog is None:
        response_json["is_starred"] = "0"
        rlog_new = ReadLog()
        rlog_new.item_id = item.id
        rlog_new.user_id = session["user_id"]
        rlog_new.is_read = 1
        rlog_new.is_starred = 0
        db.session.add(rlog_new)
        db.session.commit()
    else:
        response_json["is_starred"] = rlog.is_starred

    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/item/star', methods = ['GET'])
def getStarredItem():

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    rlog = ReadLog.query.filter(ReadLog.is_starred == 1).all()

    response_json = {}

    response_json["user"] = session["user_name"]

    item_list = []
    for aRlog in rlog:
        item = aRlog.item
        item_dict = {
            "id": item.id,
            "feed_id": item.feed_id,
            "feed_name": item.feed.name,
            "feed_url": item.feed.url,
            "feed_desc": item.feed.desc,
            "url": item.url,
            "title": item.title,
            "desc": item.guide,
            "pub_time": item.pub_time
        }
        item_list.append(item_dict)

    response_json["items"] = item_list

    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/item/<item_id>/star', methods = ['GET'])
def starItem(item_id):

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    item = Item.query.filter(Item.id == item_id).first()

    if item is None:
        return jsonify({"code": "-2"})

    rlog = ReadLog.query.filter(ReadLog.item_id == item_id).first()

    if rlog is None:
        rlog_new = ReadLog()
        rlog_new.item_id = item_id
        rlog_new.user_id = session["user_id"]
        rlog_new.is_starred = 1
        rlog_new.is_read = 0
        db.session.add(rlog_new)
        db.session.commit()
    else:
        rlog.is_starred = 1
        db.session.commit()

    return jsonify({"code": "1"})

