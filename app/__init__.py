from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

grosus = Flask(__name__)
grosus.config.from_object('config')
db = SQLAlchemy(grosus)

from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.init_app(grosus)

from app import views, models
