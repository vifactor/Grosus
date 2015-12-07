from flask import Flask

grosus = Flask(__name__)
grosus.config.from_object('config')

from app import views
