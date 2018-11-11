from flask import jsonify, request, session
from .__init__ import api
from app.models.model import User, Category, Feed, Subscribe, Item
import feedparser
from db import db
from datetime import datetime
from app.api.config import items_num_limit, item_save_limit, item_guide_word

class apiTools:

    @staticmethod
    def isLogin():
        if 'user_id' not in session:
            return False
        else:
            return True

    @staticmethod
    def getUserModel(user_id):
        user = User.query.filter(User.id == user_id).first()
        return user

    @staticmethod
    def getUserName(user_id):
        user = User.query.filter(User.id == user_id).first()

        if user is None:
            return None
        else:
            return user.nickname


    @staticmethod
    def getFeedByUrl(url):
        return feedparser.parse(url)


    @staticmethod
    def getFeedByIdFromDB(id):
        return Feed.query.filter(Feed.id == id).first()

    @staticmethod
    def saveItemByFeed(feedpar, feed_id):

        try:
            counter = 0
            for item_info in feedpar["entries"]:
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
                if counter == items_num_limit:
                    break

            db.session.commit()

            return True

        except Exception as e:
            print("Error in apiTools.saveItemByFeed: ", e)
            return False

    @staticmethod
    def getFeedByUrlFromDB(rss_url):

        feed_old = Feed.query.filter(Feed.url == rss_url).first()

        if feed_old is not None:
            # 数据库里有此rss源
            return feed_old
        else:
            # 数据库里没有，新建
            rss_feed = apiTools.getFeedByUrl(rss_url)
            if rss_feed is None:
                return None

            feed_old = Feed.query.filter(Feed.url == rss_feed["feed"]["title_detail"]["base"]).first()
            if feed_old is not None:
                return feed_old

            feed_new = Feed()
            feed_new.url = rss_feed["feed"]["title_detail"]["base"]
            feed_new.name = rss_feed["feed"]["title"]
            feed_new.desc = rss_feed["feed"]["subtitle"]
            update_time = rss_feed["feed"]["updated_parsed"]
            if update_time is None:
                feed_new.last_fetch = datetime.now()
            else:
                feed_new.last_fetch = datetime(*update_time[0:6])
            db.session.add(feed_new)
            db.session.commit()

            feed_new = Feed.query.filter(Feed.url == rss_feed["feed"]["title_detail"]["base"]).first()

            try_count = 0
            while(True):
                item_save_flag = apiTools.saveItemByFeed(rss_feed, feed_new.id)
                if item_save_flag is True:
                    break
                else:
                    try_count += 1
                    if try_count == item_save_limit:
                        return False


            return feed_new
