from app import grosus, db, login_manager
from flask import render_template, redirect, flash, url_for, g
from flask.ext.login import login_required, login_user, current_user, logout_user
from .forms import LoginForm
from .models import User, Law, Deputy
from config import LAWS_PER_PAGE, DEPUTIES_PER_PAGE

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@grosus.before_request
def before_request():
   g.user = current_user


@grosus.route('/')
@grosus.route('/index')
@login_required
def index():
    user = {'nickname': 'Musterman'} # fake user
    return render_template('index.html',
                          title='Home',
                          user=user)

@grosus.route('/deputies')
@grosus.route('/deputies/<int:page>')
@login_required
def deputies(page=1):
    deputies = Deputy.query.paginate(page, DEPUTIES_PER_PAGE, True)
    return render_template('deputies.html',
                          title='Deputies',
                          deputies=deputies)

@grosus.route('/laws')
@grosus.route('/laws/<int:page>')
@login_required
def laws(page=1):
    laws = Law.query.paginate(page, LAWS_PER_PAGE, True)
    return render_template('laws.html',
                          title='Laws',
                          laws=laws)
                          
@grosus.route('/support/<int:law_id>')
@login_required
def support(law_id):
    """This method allows the current user to add record to a database that law 
    with law_id is supported by him"""
    print(g.user, "supported law: %d" % law_id)
    return redirect(url_for('laws'))
    
@grosus.route('/reject/<int:law_id>')
@login_required
def reject(law_id):
    """This method allows the current user to add record to a database that law 
    with law_id is not supported by him"""
    print("User %s rejected law: %d" % (current_user.login, law_id))
    return redirect(url_for('laws'))

@grosus.route('/ignore/<int:law_id>')
@login_required
def ignore(law_id):
    """This method allows the current user to add record to a database that law 
    with law_id is ignored by him"""
    print("User %s ignored law: %d" % (current_user.login, law_id))
    return redirect(url_for('laws'))

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
