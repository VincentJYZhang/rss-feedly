import uuid
from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from db import db


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nickname = db.Column(db.String(64))  # 昵称
    password = db.Column(db.String(64))  # 密码
    email = db.Column(db.String(80))  # 电子游戏地址
    vertification = db.Column(db.Integer, default=0)  # 邮件是否认证
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', uselist=True, backref='user')
    subscribe = db.relationship('Subscribe', backref='user')
    readlog = db.relationship('ReadLog', backref='user')

    def __repr__(self):
        return '<User {}> - {}'.format(self.username, self.id)


class Feed(db.Model):  # 订阅源
    __tablename__ = 'feed'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    url = db.Column(db.String(255), unique=True, index=True)  # feed url
    name = db.Column(db.VARCHAR(120))  # feed name
    desc = db.Column(db.VARCHAR(255))  # feed description
    last_fetch = db.Column(db.DateTime)  # last fetch time
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    subscribe = db.relationship('Subscribe', backref='feed')
    collect = db.relationship('Collect', backref='feed')
    item = db.relationship('Item', backref='feed')

    def __repr__(self):
        return '<Feed {}>'.format(self.url)


class Item(db.Model):  # 每个订阅源的更新内容
    __tablename__ = 'items'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    url = db.Column(db.String(255))  # item url
    feed_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('feed.id'))  # 外键
    author = db.Column(db.String(64))  # author of item
    guide = db.Column(db.String(100))  # guide of item
    title = db.Column(db.String(64))  # title of item
    content = db.Column(db.Text)  # content of item
    pub_time = db.Column(db.DateTime)  # publish time of item
    fetch_time = db.Column(db.DateTime)  # last fetch time
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    readlog = db.relationship('ReadLog', backref='item')

    def __repr__(self):
        return '<Item {}>'.format(self.url)


class Subscribe(db.Model):  # 用户订阅
    __tablename__ = 'subscribe'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    feed_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('feed.id'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}> - <Feed {}>'.format(self.user_id, self.feed_id)


class Category(db.Model):  # 收藏目录
    __tablename__ = 'category'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))  # user.id外键
    category_name = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    collect = db.relationship('Collect', backref='category')


class ReadLog(db.Model):  # 阅读记录
    __tablename__ = 'readlog'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    item_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('items.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))

    is_starred = db.Column(db.Integer, default=0)  # 是否收藏
    is_read = db.Column(db.Integer, default=0)  # 是否已读
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Collect(db.Model):  # 用户收藏
    __tablename__ = 'collect'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)  # primary key
    category_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('category.id'))
    feed_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('feed.id'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)