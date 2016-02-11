WTF_CSRF_ENABLED = True
SECRET_KEY = 'my-secret-key-value'

# database stuff
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'grosus.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

LAWS_PER_PAGE = 3
DEPUTIES_PER_PAGE = 8
