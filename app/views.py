from app import grosus, db, login_manager
from flask import render_template, redirect, flash, url_for
from flask.ext.login import login_required, login_user, current_user, logout_user
from .forms import LoginForm
from .models import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@grosus.route('/')
@grosus.route('/index')
@login_required
def index():
    user = {'nickname': 'Musterman'} # fake user
    return render_template('index.html',
                          title='Home',
                          user=user)

@grosus.route('/deputies')
@login_required
def deputies():
    deputies = [{'name': 'Musterman', 'group': 'Communists'}, # fake deputies
                {'name': 'Muller', 'group': 'Liberals'},
                {'name': 'Smith', 'group': 'Democrats'},
                {'name': 'Smith', 'group': 'Democrats'},
                {'name': 'Smith', 'group': 'Democrats'}, {'name': 'Smith', 'group': 'Democrats'}]
    return render_template('deputies.html',
                          title='Deputies',
                          deputies=deputies)

@grosus.route('/laws')
@login_required
def laws():
    laws = [1, 2, 3, 4, 5]
    return render_template('laws.html',
                          title='Laws',
                          laws=laws)

@grosus.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for "%s"' % form.login.data)
        # create new user and add it to database if not existed
        user = User.query.filter_by(login=form.login.data).first()
        if user is None:
            user = User(login=form.login.data)
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html',
                           title='Sign in',
                           form=form)

@grosus.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))
