'''
    Create on 2018.09
'''

from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from db import db
import pymysql
from config import db_url

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.secret_key = r'_9#z3L"FdQ8z\n\xrc]/'

    pymysql.install_as_MySQLdb()

    with app.app_context():
        db.init_app(app)
        from app.models.model import User, Category, Collect, Subscribe, Item, Feed, ReadLog
        db.create_all()

    register_blueprint(app)
    return app

def register_blueprint(app):
    from app.web.__init__ import web
    from app.api.__init__ import api
    app.register_blueprint(web)
    app.register_blueprint(api)