import random
from zKM_Test.Backend.app import APP_MAIN, APPLOGIN, db, forms,model
from zKM_Test.Backend.app.model import User, Gre_data, Country
from zKM_Test.Backend.app.forms import LoginForm,RegistrationForm, EditProfileForm,AdditionalForm
from flask import render_template, flash, redirect, url_for, abort, session, make_response
from flask_oauth import OAuth
from flask_login import current_user, login_user, logout_user , login_required, fresh_login_required
from flask_register import register_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from flask import request
from datetime import datetime
import json,os
from flask_oauth import OAuth
from urllib.request import Request,urlopen,URLError
from os import urandom
from PIL import Image
next_gpage = ""
reg_bool = True
GOOGLE_CLIENT_ID = '375961356325-p3umdlkkjr6ak9kairqv8b3ttalio52a.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '8UggTqBUxM3M-9cd8KtLv8Tj'
REDIRECT_URI = '/oauth2callback'



oauth = OAuth()


google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)



@APP_MAIN.route('/gsign')
@APPLOGIN.header_loader
def gsign():
    global reg_bool
    reg_bool=False

    #access_token = session.get('access_token')
    if session.get('access_token') is None:
        print("access_token???")
        return redirect(url_for('login1'))
    access_token = session.get('access_token')[0]
    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    print(headers)
    print(req)

    try:
        res = urlopen(req)
        res = res.read().decode('utf-8')
        res = json.loads(res)
        uemail = res['email']

    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    user = User.objects(email=uemail)
    if len(user) == 0:
        print("painiiiii")
        session.pop('access_token',None)
        return redirect(url_for('login'))
    else:
        print("paiceeeeeeeeeeee")
        user = user[0]
        login_user(user)
        global next_gpage
        next_page = next_gpage
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)


@APP_MAIN.route('/login1')
def login1():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@APP_MAIN.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    print("ekhane ashco?")
    global reg_bool
    if reg_bool==False:
        return redirect(url_for('gsign'))
    else:
        return redirect(url_for('gregister'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@APP_MAIN.route('/')
@APP_MAIN.route('/index')
def index():
    posts = [
        {
            'author': {'username':'Koushik Deb'},
            'body': 'Beautiful day in Malibagh'
        },
        {
            'author': {'username':'Sadeen Mahbub Mob'},
            'body': 'The Justice League movie was so khuul!'
        }
    ]
    return render_template('index.html', title = 'Home', posts=posts)


@APP_MAIN.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password_hash=generate_password_hash(form.password.data),reg_date=datetime.utcnow())
        user.save()
        flash('Congratulation, you are now a member of GRE-Web App!!')
        session.pop('access_token', None)
        return redirect(url_for('additional',username=form.username.data))

    return render_template('register.html', title = 'Register', form=form)


@APP_MAIN.route('/gregister', methods=['POST','GET'])
def gregister():
    global reg_bool
    reg_bool = True
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login1'))
    access_token = access_token[0]
    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
        res = res.read().decode('utf-8')
        res = json.loads(res)
        upic = res['picture']
        uemail = res['email']

    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('register'))
        return res.read()

    form = RegistrationForm()
    form.email.data=uemail
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password_hash=generate_password_hash(form.password.data),reg_date=datetime.utcnow(),upic=upic)
        user.save()
        flash('Congratulation, you are now a member of GRE-Web App!!')
        session.pop('access_token',None)
        return redirect(url_for('additional',username=form.username.data))

    return render_template('register.html', title = 'Register', form=form)


@APP_MAIN.route('/additional/<username>', methods=['POST','GET'])
@register_required
def additional(username):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = AdditionalForm()

    collection = db['country']
    cursor = collection.find({})
    arr = []
    for i in cursor:
        arr.append(i['country_name'])
    if form.validate_on_submit():
        user = User.objects(username=username)
        if len(user)==0:
            return render_template(url_for('login'))
        else:
            user = user[0]
        if user.check_password(form.confirm_password.data):
            user = user.update(age=form.age.data,
                               country=request.form.get('cnt_name'),
                               gender=form.gender.data)
            return redirect(url_for('login'))
        else:
            return redirect(url_for('index'))
    return render_template('additional.html',form=form , arr = arr)


@APP_MAIN.route('/login', methods=['POST','GET'])
def login():
    global next_gpage
    next_gpage = request.args.get('next')
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data)
        if len(user)==0:
            return redirect(url_for('login'))
        else:
            user = user[0]
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title="Sign In", form=form)


@APP_MAIN.route('/about')
def about():
    return render_template('about.html', title = 'About')


@APP_MAIN.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    if request.cookies.get('session'):
        resp.set_cookie('session', '', expires=0)
        session.pop('access_token',None)
    logout_user()
    return resp
    #return redirect(url_for('index'))


@APP_MAIN.route('/user/<username>')
@login_required
def user(username):
    user = User.objects(username=username)
    if(len(user)==0):
        abort(404)
    else:
        user=user[0]
        if current_user.pic is not None:
            user.pic = url_for('static',filename='img/' + current_user.pic)
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

def save_pic(form_picture):
    random_hex = urandom(8).hex()
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(APP_MAIN.static_folder, 'img', picture_fn)
    output_size=(125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@APP_MAIN.route('/edit_profile',methods=['POST','GET'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_pic(form.pic.data)
            current_user.update(pic=picture_file)
        current_user.update(about_me=form.about_me.data)
        current_user.reload()
        flash("Your changes have been saved! No one cares, by the way!")
        return redirect(url_for('user', username=current_user.username))
    elif request.method=='GET':
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',title="Edit Profile", form = form)


@APP_MAIN.route('/dictionary')
@login_required
def dictionary():
    pass


@APP_MAIN.route('/test')
@login_required
def test():
    pass



@APP_MAIN.route('/practice')
@login_required
def practice():
    pass


@APP_MAIN.route('/stat')
@login_required
def stat():
    col = db['gre_data']
    cursor = col.find({})

    stat_data = Gre_data.objects(username=current_user.username)
    stat_data = stat_data[0]

    return render_template('stat.html',history = stat_data
                            .history, how_many_test = stat_data.how_many_test+1)


@APP_MAIN.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update(last_seen=datetime.utcnow())
        current_user.reload();