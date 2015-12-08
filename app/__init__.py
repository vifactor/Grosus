from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

grosus = Flask(__name__)
grosus.config.from_object('config')
db = SQLAlchemy(grosus)

from app import views, models
