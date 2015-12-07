from app import grosus
from flask import render_template

@grosus.route('/')
@grosus.route('/index')
def index():
    user = {'nickname': 'Musterman'} # fake user
    return render_template('index.html',
                          title='Home',
                          user=user)
