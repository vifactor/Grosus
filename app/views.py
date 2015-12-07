from app import grosus
from flask import render_template, redirect, flash
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
    if form.validate_on_submit():
        flash('Login requested for "%s"' % form.login.data)
        return redirect('/index')
    return render_template('login.html',
                           title='Sign in',
                           form=form)
