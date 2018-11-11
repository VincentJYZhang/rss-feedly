from flask import jsonify, request, session
from .__init__ import api
from db import db
from datetime import datetime
from .tools import apiTools
from app.models.model import Feed, Subscribe, Item, ReadLog
from app.api.config import item_update_limit, feed_getItem_limit, item_guide_word

@api.route('/feed', methods = ['POST'])
def addFeed():

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    rss_url = request.headers["url"]

    feed_old = apiTools.getFeedByUrlFromDB(rss_url)

    if feed_old is None:
        return jsonify({"code": "-2"})

    sub = Subscribe.query.filter(Subscribe.user_id == session["user_id"], Subscribe.feed_id == feed_old.id).first()

    if sub is not None:
        return jsonify({"code": "1"})

    subcribe_new = Subscribe()
    subcribe_new.user_id = session["user_id"]
    subcribe_new.feed_id = feed_old.id
    db.session.add(subcribe_new)
    db.session.commit()

    return jsonify({"code": "1"})

@api.route('/feed/<feed_id>/delete', methods=['GET'])
def deleteFeedFromDBv2(feed_id):

    feed_old = apiTools.getFeedByIdFromDB(feed_id)

    for item in feed_old.item:
        for rlog in item.readlog:
            db.session.delete(rlog)

        db.session.delete(item)

    for sub in feed_old.subscribe:
        db.session.delete(sub)

    for col in feed_old.collect:
        db.session.delete(col)

    db.session.delete(feed_old)

    db.session.commit()

    return jsonify({"code": "1"})


@api.route('/feed', methods = ['GET'])
def getFeedList():

    response_json = {}
    if apiTools.isLogin() == False:
        response_json["code"] = "-1"
        return jsonify(response_json)

    response_json["user"] = session["user_name"]

    feed_list = []

    user = apiTools.getUserModel(session["user_id"])

    for aSub in user.subscribe:
        aFeed = aSub.feed
        feed_dict = {"id": aFeed.id, "url": aFeed.url, "name": aFeed.name, "desc": aFeed.desc, "last_fetch": aFeed.last_fetch}
        feed_list.append(feed_dict)

    response_json["feeds"] = feed_list

    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/feed/<feed_id>', methods=['GET'])
def getFeed(feed_id):

    feed_old = apiTools.getFeedByIdFromDB(feed_id)

    if feed_old is None:
        return jsonify({"code":"-1"})

    response_json = {}
    response_json["name"] = feed_old.name
    response_json["url"] = feed_old.url
    response_json["id"] = feed_old.id
    response_json["desc"] = feed_old.desc

    item_list = []

    counter = 0

    for item in feed_old.item:
        rlog = ReadLog.query.filter(ReadLog.item_id == item.id).first()

        item_dict = {"id": item.id, "url": item.url,
                     "author": item.author, "guide": item.guide, "title": item.title,
                     "pub_time": item.pub_time}

        if rlog is None:
            item_dict["is_starred"] = "0"
            item_dict["is_read"] = "0"
        else:
            item_dict["is_starred"] = rlog.is_starred
            item_dict["is_read"] = rlog.is_read

        item_list.append(item_dict)

        counter += 1
        if counter >= feed_getItem_limit:
            break

    response_json["items"] = item_list
    response_json["code"] = "1"

    return jsonify(response_json)


@api.route('/feed/search', methods=['GET'])
def searchFeed():

    all_results = Feed.query.filter(Feed.name.like("%" + request.headers["key"] + "%")).all()

    result_list = []

    for feed in all_results:
        feed_dict = {"feed_name": feed.name, "feed_url": feed.url, "feed_desc": feed.desc}
        result_list.append(feed_dict)

    response_json = {}
    response_json["code"] = "1"
    response_json["result"] = result_list

    return jsonify(response_json)


@api.route('/feed/<feed_id>/update', methods = ['GET'])
def updateFeed(feed_id):

    feed = apiTools.getFeedByIdFromDB(feed_id)

    if feed is None:
        return jsonify({"code": "-1"})

    feedpar = apiTools.getFeedByUrl(feed.url)

    counter = 0
    for item_info in feedpar["entries"]:

        item_old = Item.query.filter(Item.url == item_info["link"]).first()
        if item_old is not None:
            continue
        item_new = Item()
        item_new.url = item_info["link"]
        item_new.feed_id = feed_id
        item_new.author = item_info.get("author")
        item_new.guide = item_info["summary"][0:item_guide_word]
        item_new.title = item_info["title"]
        item_new.content = item_info["summary"]
        item_new.pub_time = datetime(*item_info["published_parsed"][0:6])
        item_new.fetch_time = datetime.utcnow()
        db.session.add(item_new)
        counter += 1
        if counter == item_update_limit:
            break

    db.session.commit()

    return jsonify({"code": "1"})


@api.route('/feed/<feed_id>', methods = ['DELETE'])
def deleteFeedFromUser(feed_id):

    if apiTools.isLogin() == False:
        return jsonify({"code": "-1"})

    sub_old = Subscribe.query.filter(Subscribe.feed_id == feed_id, Subscribe.user_id == session["user_id"]).first()

    if sub_old is None:
        return jsonify({"code": "-2"})

    db.session.delete(sub_old)
    db.session.commit()

    return jsonify({"code": "1"})


@api.route('/delete/feed/<feed_id>')
def deleteFeedFromDB(feed_id):

    feed_old = Feed.query.filter(Feed.id == feed_id).first()

    if feed_old is None:
        return jsonify({"code": "-1"})


    for coll in feed_old.collect:
        db.session.delete(coll)

    for sub in feed_old.subscribe:
        db.session.delete(sub)

    for item in feed_old.item:

        for readlog in item.readlog:
            db.session.delete(readlog)

        db.session.delete(item)

    db.session.delete(feed_old)

    db.session.commit()

    return jsonify({"code": "1"})



@api.route('/feed/star', methods = ['GET'])
def getStar():
    pass

