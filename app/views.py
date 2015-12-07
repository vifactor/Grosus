from app import grosus
from flask import render_template
from .forms import LoginForm

@grosus.route('/')
@grosus.route('/index')
def index():
    user = {'nickname': 'Musterman'} # fake user
    return render_template('index.html',
                          title='Home',
                          user=user)

@grosus.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html',
                           title='Sign in',
                           form=form)
