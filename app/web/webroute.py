from flask import jsonify, request, session, render_template, redirect
from .__init__ import web
from app.api.feed_api import getFeedList, getFeed
from app.api.category_api import getCategoryList
from app.api.item_api import getItem
from app.models.model import Category, Feed, Collect
import json
import re


@web.route('/')
def root():
    if "user_id" in session:
        return redirect('/category')
    else:
        return redirect('/login')


@web.route('/login', methods=["GET"])
def loginWeb():
    return render_template("login.html")


@web.route('/register')
def registerWeb():
    return render_template("register.html")


@web.route('/category')
def getWebCategory():
    if 'user_id' in session:
        cate = getCategoryList()
        cate = json.loads(cate.data)
        return render_template("cateory.html",
                               usermail=session["user_mail"],
                               username = session["user_name"],
                               categories = cate["list"]
                               )
    else:
        return render_template("feed.html")


@web.route('/feed')
def getWebFeed():
    feed_response = getFeedList()
    # print(feed_response.data)
    feed_response = json.loads(feed_response.data)
    # print(feed_response)
    if feed_response["feeds"] is False:
        return render_template("feed.html")
    return render_template("feed.html", feeds=feed_response["feeds"], usermail=session["user_mail"], username=session["user_name"])


@web.route('/feed/<feed_id>')
def getWebAFeed(feed_id):
    pass

@web.route('/category/feed/<feed_id>')
def getWebFeedContent(feed_id):
    return redirect("/")


@web.route('/category/<int:cate_id>/feed/<feed_id>')
def getFeedInCategory(cate_id, feed_id):
    if 'user_id' in session:
        coll = Collect.query.filter(Collect.category_id == cate_id, Collect.feed_id == feed_id).first()
        if coll is None:
            return redirect('/category')
        cate = getCategoryList()
        cate = json.loads(cate.data)
        feed = getFeed(feed_id)
        feed = json.loads(feed.data)
        return render_template("cateory.html",
                               usermail=session["user_mail"],
                               username = session["user_name"],
                               categories = cate["list"],
                               cate_id = cate_id,
                               items = feed["items"],
                               feed_id = feed_id,
                               feed_name = feed["name"],
                               feed_desc = feed["desc"]
                               )
    else:
        return redirect("/")


@web.route('/item/<item_id>')
def getWebAItem(item_id):
    item = getItem(item_id)
    item = json.loads(item.data)

    if item["code"] == "1":
        return render_template("item.html",
                               usermail=session["user_mail"],
                               username=session["user_name"],
                               item = item)
    else:
        return render_template("item.html")