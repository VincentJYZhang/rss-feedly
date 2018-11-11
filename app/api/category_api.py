from flask import jsonify, request, session
from .__init__ import api
from app.models.model import User, Category, Collect, Subscribe
from .tools import apiTools
from db import db

@api.route('/category/<cate_id>/feed/<feed_id>', methods=['DELETE'])
def deleteFeedFromCategory(cate_id, feed_id):

    if apiTools.isLogin() == False:
        return jsonify({"code":"-1"})

    cate = Category.query.filter(Category.id == cate_id, Category.user_id == session["user_id"]).first()
    if cate is None:
        return jsonify({"code": "-2"})

    coll_old = Collect.query.filter(Collect.feed_id == feed_id, Collect.category_id == cate_id).first()
    if coll_old is None:
        return jsonify({"code": "-3"})

    db.session.delete(coll_old)
    db.session.commit()

    return jsonify({"code": "1"})


@api.route('/category', methods=['POST'])
def addCategory():

    cate_name = request.headers["name"]

    response_json = {}
    if apiTools.isLogin() == False:
        response_json["code"] = "-1"
        return jsonify(response_json)

    cate_old = Category.query.filter(Category.user_id == session["user_id"], Category.category_name == cate_name).first()

    if cate_old is not None:
        response_json["code"] = "-2"
        return jsonify(response_json)

    cate_new = Category()
    cate_new.user_id = session["user_id"]
    cate_new.category_name = cate_name
    db.session.add(cate_new)
    db.session.commit()

    response_json["code"] = "1"

    return jsonify(response_json)

@api.route('/category', methods = ['GET'])
def getCategoryList():

    response_json = {}
    if apiTools.isLogin() == False:
        response_json["code"] = "-1"
        return jsonify(response_json)

    response_json["user"] = session["user_name"]

    cate_list = []

    user = apiTools.getUserModel(session["user_id"])

    for cate in user.category:
        feed_list = []
        for collect in cate.collect:
            feed = collect.feed
            feed_dict = {"id": feed.id, "name": feed.name, "url": feed.url, "desc": feed.desc, "last-fetch": feed.last_fetch}
            feed_list.append(feed_dict)
        temp_dict = {"name": cate.category_name, "id": cate.id, "feeds": feed_list}
        cate_list.append(temp_dict)

    response_json["list"] = cate_list

    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/category/<cate_id>', methods = ['POST'])
def addFeedToCategory(cate_id):

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    cate = Category.query.filter(Category.id == cate_id, Category.user_id == session["user_id"]).first()

    if cate is None:
        return jsonify({"code": "-2"})

    if "id" in request.headers:
        feed = apiTools.getFeedByIdFromDB(request.headers["id"])
    elif "url" in request.headers:
        feed = apiTools.getFeedByUrlFromDB(request.headers["url"])
    else:
        return jsonify({"code": "0"})

    if feed == False:
        return jsonify({"code": "0"})

    sub = Subscribe.query.filter(Subscribe.user_id == session["user_id"], Subscribe.feed_id == feed.id).first()

    if sub is None:
        subcribe_new = Subscribe()
        subcribe_new.user_id = session["user_id"]
        subcribe_new.feed_id = feed.id
        db.session.add(subcribe_new)

    coll_old = Collect.query.filter(Collect.feed_id == feed.id, Collect.category_id == cate.id).first()

    if coll_old is not None:
        return jsonify({"code": "1"})

    coll = Collect()

    coll.category_id = cate_id
    coll.feed_id = feed.id

    db.session.add(coll)
    db.session.commit()

    return jsonify({"code": "1"})


@api.route('/category/<cate_id>', methods=['GET'])
def getCategory(cate_id):
    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    cate = Category.query.filter(Category.id == cate_id, Category.user_id == session["user_id"]).first()

    if cate is None:
        return jsonify({"code": "-2"})

    response_json = {}
    response_json["name"] = cate.category_name
    response_json["user"] = session["user_name"]

    feed_list = []
    for coll in cate.collect:
        feed = coll.feed
        feed_dict = {"id": feed.id, "name": feed.name, "url": feed.url, "desc": feed.desc, "last_fetch": feed.last_fetch}
        feed_list.append(feed_dict)

    response_json["feeds"] = feed_list

    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/category/<cate_id>', methods = ['DELETE'])
def deleteCategory(cate_id):

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    cate = Category.query.filter(Category.id == cate_id, Category.user_id == session["user_id"]).first()

    if cate is None:
        return jsonify({"code": "-2"})

    for coll in cate.collect:
        db.session.delete(coll)

    db.session.delete(cate)

    db.session.commit()

    return jsonify({"code": "1"})



