import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_socketio import SocketIO, join_room
import os

app = Flask(__name__)

"""
Application configuration.
Using os.environ.get because this project is hosted on Heroku
Heroku allow you to specify those parameter
"""
app.debug = os.environ.get('DEBUG')
app.config['SECRET_KEY'] = os.environ.get('SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
db = SQLAlchemy(app)

"""
Using Session to store user sessions.
"""
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

"""
Using SocketIO for Instant Messaging.
"""
socketio = SocketIO(app)


class User(db.Model):
    """
    User Model
    user_id: Int, PK
    user_name: String(50)
    user_email_id: String(100)
    user_password: String(100) stored encrypted by werkzeug.security
    user_status: String(100)
    """
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50))
    user_email_id = db.Column(db.String(100))
    user_password = db.Column(db.String(100))
    user_status = db.Column(db.String(100))

    def __init__(self, user_name, user_email_id, user_password, user_status):
        self.user_name = user_name
        self.user_email_id = user_email_id
        self.user_password = user_password
        self.user_status = user_status


class Relation(db.Model):
    """
    Relation Model
    relation_id: Int, PK
    mutual_id: String(50)
        Format: min(relation_user_id_1, relation_user_id_2) + ':' + max((relation_user_id_1, relation_user_id_2))
    relation_user_id_1: Int, FK(User Table)
    relation_user_id_2: Int, FK(User Table)
    relation_status: String(50) (unknown, friend)
    """
    __tablename__ = 'relation'
    relation_id = db.Column(db.Integer, primary_key=True)
    mutual_id = db.Column(db.String(50))
    relation_user_id_1 = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    relation_user_id_2 = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    relation_status = db.Column(db.String(50))

    def __init__(self, relation_user_id_1, relation_user_id_2, relation_status, mutual_id):
        self.relation_user_id_1 = relation_user_id_1
        self.relation_user_id_2 = relation_user_id_2
        self.relation_status = relation_status
        self.mutual_id = mutual_id


class Request(db.Model):
    """
    Request Model
    request_id: Int, PK
    request_from_user_id: Int, FK(User Table)
    request_to_user_id: Int, FK(User Table)
    request_status: String(50) (Approved, Decline, Pending)
    """
    __tablename__ = 'request'
    request_id = db.Column(db.Integer, primary_key=True)
    request_from_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    request_to_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    request_status = db.Column(db.String(50))

    def __init__(self, request_from_user_id, request_to_user_id, request_status):
        self.request_from_user_id = request_from_user_id
        self.request_to_user_id = request_to_user_id
        self.request_status = request_status


class Message(db.Model):
    """
    Message Model
    message_id: Int, PK
    mutual_id: String(50) From Relation Table
    message_from_user_id: Int, FK(User Table)
    message_to_user_id: Int, FK(User Table)
    message: Text
    message_status: String(50)
    """
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True)
    mutual_id = db.Column(db.String(50))
    message_from_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    message_to_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    message = db.Column(db.Text)
    message_status = db.Column(db.String(50))

    def __init__(self, mutual_id, message_from_user_id, message_to_user_id, message, message_status):
        self.mutual_id = mutual_id
        self.message_from_user_id = message_from_user_id
        self.message_to_user_id = message_to_user_id
        self.message = message
        self.message_status = message_status


class Post(db.Model):
    """
    Post Model
    post_id: Int, PK
    post_from_user_id: Int FK(User Table)
    post: Text
    """
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)
    post_from_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post = db.Column(db.Text)

    def __init__(self, post_from_user_id, post):
        self.post_from_user_id = post_from_user_id
        self.post = post


def send_email(email_address, validation_url):
    """
    Function to send verification email to new users
    Without verification user cannot login
    Below configuration is for Gmail
    Using os.environ.get because this project is hosted on Heroku
    Heroku allow you to specify those parameter
    """
    sender_email = os.environ.get('EMAIL')
    receiver_email = email_address
    message = MIMEMultipart("alternative")
    message["Subject"] = "Account Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Hello,
    Thank You for registration. Please click below link to activate your account.
    """
    html = "<html><body><a href=" + validation_url + ">Click to activate</a></body></html>"
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(os.environ.get('EMAIL'), os.environ.get('PASSWORD'))
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def check_session():
    """
    Function to check if user available in session
    """
    if 'user_id' in session:
        return True
    else:
        return False


@app.route('/')
def home():
    """
    Route Function for Home page
    Only accessible when User is Logged In
    """
    if check_session():
        get_post = Post.query.filter_by(post_from_user_id=session['user_id']).order_by(Post.post_id.desc()).all()
        return render_template('index.html', postList=get_post)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route Function for Login Page
    """
    if request.method == 'GET':
        if check_session():
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        email = (request.form['user_email_id']).lower()
        password = request.form['user_password']
        get_user = User.query.filter_by(user_email_id=email).first()
        if not get_user:
            flash('Please check email or password!')
            return redirect(url_for('login'))
        else:
            if not check_password_hash(get_user.user_password, password):
                flash('Please check email or password!')
                return redirect(url_for('login'))
            if get_user.user_status != 'active':
                flash('Please check your inbox for account validation email!')
                return redirect(url_for('login'))
            session.permanent = True
            session['email'] = email
            session['username'] = get_user.user_name
            session['user_id'] = int(get_user.user_id)
            return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route Function for register page
    """
    if request.method == 'GET':
        if check_session():
            return redirect(url_for('home'))
        else:
            return render_template('register.html')
    elif request.method == 'POST':
        email = (request.form['user_email_id']).lower()
        username = request.form['user_name']
        password = request.form['user_password']
        get_user = User.query.filter_by(user_email_id=email).first()
        if get_user:
            flash('Email already in use!')
            return redirect(url_for('register'))
        else:
            token = generate_password_hash(email + username + password, method='sha256')
            new_user = User(user_email_id=email, user_name=username,
                            user_password=generate_password_hash(password, method='sha256'), user_status=token)
            send_email(email, request.host_url + 'validate_account/' + token)
            db.session.add(new_user)
            db.session.commit()
            flash('We have send you an email for account validation. Please check your email!')
            return redirect(url_for('login'))


@app.route('/validate_account/<token>')
def validate_account(token):
    """
    Route Function for Account Validation when user click link received in Email
    """
    get_user = User.query.filter_by(user_status=token).first()
    if get_user:
        get_user.user_status = 'active'
        db.session.commit()
        return redirect(url_for('login'))
    else:
        flash('Invalid activation code!')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """
    Route Function for Logout
    """
    if check_session():
        session.pop('email', None)
        session.pop('username', None)
        session.pop('user_id', None)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/post', methods=['GET', 'POST'])
def post():
    """
    Route Function for Post
    GET: get user post
    POST: save new post and return json response for AJAX
    """
    if check_session():
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            new_post = Post(post_from_user_id=session['user_id'], post=request.form['post'])
            db.session.add(new_post)
            db.session.commit()
            get_post = Post.query.filter_by(post_from_user_id=session['user_id']).order_by(Post.post_id.desc()).all()
            return jsonify('', render_template('ajax_post.html', postList=get_post))
    else:
        return redirect(url_for('login'))


@app.route('/friends')
def friend():
    """
    Route Function for fetching Friend List and Request List
    """
    if check_session():
        get_friends = db.session.query(Relation, User). \
            filter((Relation.relation_user_id_1 == session['user_id']) &
                   (Relation.relation_user_id_2 == User.user_id) &
                   (Relation.relation_status == 'Friend')).all()

        get_requests = db.session.query(Request, User). \
            filter((Request.request_from_user_id == User.user_id) &
                   (Request.request_to_user_id == session['user_id']) &
                   (Request.request_status == 'Pending')).all()

        return render_template('friend.html', friendList=get_friends, requestList=get_requests)
    else:
        return redirect(url_for('login'))


@app.route('/search')
def search():
    """
    Route Function for fetching all User List for finding and adding friends
    """
    if check_session():
        get_friend_id = db.session.query(Relation.relation_user_id_2). \
            filter((Relation.relation_user_id_1 == session['user_id']) &
                   (Relation.relation_status == 'Friend'))
        get_people = User.query.filter((~User.user_id.in_(get_friend_id)) &
                                       (User.user_id != session['user_id']) &
                                       (User.user_status == 'active')).all()

        return render_template('find_people.html', peopleList=get_people)
    else:
        return redirect(url_for('login'))


@app.route('/send_request/<user_id>')
def send_request(user_id):
    """
    Route Function for sending request
    AJAX used to register request and display output
    """
    if check_session():
        check_request = Request.query.filter((Request.request_from_user_id == session['user_id']) &
                                             (Request.request_to_user_id == user_id)).first()
        if check_request:
            if check_request.request_status == 'Pending':
                return jsonify('', render_template('ajax_request_result.html', request_result='warning',
                                                   request_text='Request Already Exist'))
            else:
                check_request.request_status = 'Pending'
                db.session.commit()
                return jsonify('', render_template('ajax_request_result.html', request_result='warning',
                                                   request_text='Request Sent Again'))
        else:
            add_request = Request(request_from_user_id=session['user_id'], request_to_user_id=user_id,
                                  request_status='Pending')
            db.session.add(add_request)
            db.session.commit()
            return jsonify('', render_template('ajax_request_result.html', request_result='success',
                                               request_text='Request Send'))
        return render_template('find_people.html')
    else:
        return redirect(url_for('login'))


@app.route('/modify_request/<answer>/<request_id>')
def modify_request(answer, request_id):
    """
    Route Function for modifying request
    Used to register accept or decline of request
    """
    if check_session():
        check_request = Request.query.filter((Request.request_to_user_id == session['user_id']) &
                                             (Request.request_id == request_id) &
                                             (Request.request_status == 'Pending')).first()
        if check_request:
            if answer == 'accept':
                check_request.request_status = 'Approved'
                db.session.commit()
                if session['user_id'] < check_request.request_from_user_id:
                    mutual_id_ = str(session['user_id']) + ':' + str(check_request.request_from_user_id)
                else:
                    mutual_id_ = str(check_request.request_from_user_id) + ':' + str(session['user_id'])

                add_relation = Relation(relation_user_id_1=session['user_id'],
                                        relation_user_id_2=check_request.request_from_user_id,
                                        relation_status='Friend', mutual_id=mutual_id_)
                db.session.add(add_relation)
                db.session.commit()
                add_relation = Relation(relation_user_id_2=session['user_id'],
                                        relation_user_id_1=check_request.request_from_user_id,
                                        relation_status='Friend', mutual_id=mutual_id_)
                db.session.add(add_relation)
                db.session.commit()
                get_user = User.query.filter_by(user_id=check_request.request_from_user_id).first()
                return jsonify('', render_template('ajax_request_action.html', request_result='success',
                                                   friend=get_user, request_text='Accepted'))
            else:
                check_request.request_status = 'Decline'
                db.session.commit()
                return jsonify('', render_template('ajax_request_action.html', request_result='warning',
                                                   friend='None', request_text='Declined'))
        else:
            return jsonify('', render_template('ajax_request_action.html', request_result='warning',
                                               friend='None', request_text='No such request'))
    else:
        return redirect(url_for('login'))


@app.route('/remove/<user_id>')
def remove_friend(user_id):
    """
    Route Function for removing user from friend list
    """
    if check_session():
        check_user = Relation.query.filter((Relation.relation_user_id_1 == session['user_id']) &
                                           (Relation.relation_user_id_2 == user_id) &
                                           (Relation.relation_status == 'Friend')).first()
        if check_user:
            check_user.relation_status = 'Not Friend'
            db.session.commit()
            check_user = Relation.query.filter((Relation.relation_user_id_2 == session['user_id']) &
                                               (Relation.relation_user_id_1 == user_id) &
                                               (Relation.relation_status == 'Friend')).first()
            if check_user:
                check_user.relation_status = 'Not Friend'
                db.session.commit()
            return redirect(url_for('friend'))
        else:
            return redirect(url_for('friend'))
    else:
        return redirect(url_for('login'))


@app.route('/friend_page/<user_id>')
def friend_page(user_id):
    """
    Route Function for visiting friend page and viewing their post
    """
    if check_session():
        check_user = Relation.query.filter((Relation.relation_user_id_1 == session['user_id']) &
                                           (Relation.relation_user_id_2 == user_id) &
                                           (Relation.relation_status == 'Friend')).first()
        if check_user:
            get_user = User.query.filter_by(user_id=user_id).first()
            get_post = Post.query.filter_by(post_from_user_id=user_id).order_by(Post.post_id.desc()).all()

            get_messages = Message.query.filter_by(mutual_id=check_user.mutual_id).all()

            return render_template('friend_home.html', userInfo=get_user, postList=get_post,
                                   mutualId=check_user.mutual_id, messageList=get_messages)

        else:
            return redirect(url_for('friend'))
    else:
        return redirect(url_for('login'))


@socketio.on('send_message')
def send_message(data):
    """
    SocketIO Function for messaging
    Receive msg from one user in room
    Store msg in database
    Send msg to another user in room
    """
    add_message = Message(message_to_user_id=data['user_to'], message_from_user_id=session['user_id'],
                          message_status='sent', message=data['message'], mutual_id=data['room'])
    db.session.add(add_message)
    db.session.commit()
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room(data):
    """
    SocketIO Function for creating room for two users
    """
    join_room(data['room'])


if __name__ == '__main__':
    db.create_all()
    app.run()
