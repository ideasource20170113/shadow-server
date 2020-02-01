import hashlib
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from shadow.extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(128))
    email = db.Column(db.String(254), unique=True, nullable=False)
    nickname = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    email_hash = db.Column(db.String(128))

    agents = db.relationship('Agent', back_populates='user', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_email_hash()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_hash(self):
        if self.email is not None and self.email_hash is None:
            self.email_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()  # encode for py23 compatible

    @property
    def is_admin(self):
        return self.email == current_app.config['SHADOW_ADMIN_EMAIL']


class Agent(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    display_name = db.Column(db.String(100))
    last_online = db.Column(db.DateTime())
    operating_system = db.Column(db.String(100))
    remote_ip = db.Column(db.String(100))
    geolocation = db.Column(db.String(100))
    output = db.Column(db.Text(), default="")
    hostname = db.Column(db.String(100))
    username = db.Column(db.String(100))

    user_email = db.Column(db.Integer, db.ForeignKey('user.email'))
    user = db.relationship('User', back_populates='agents')

    def __init__(self, uid):
        self.id = uid
        self.display_name = self.id

    def push_command(self, cmdline):
        cmd = Command()
        cmd.agent = self
        cmd.cmdline = cmdline
        cmd.timestamp = datetime.now()
        db.session.add(cmd)
        db.session.commit()

    def rename(self, new_name):
        self.display_name = new_name
        db.session.commit()

    def is_online(self):
        return (datetime.now() - self.last_online).seconds < 30


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agent_id = db.Column(db.Integer(), db.ForeignKey('agent.id'))
    agent = db.relationship('Agent', backref=db.backref('command', lazy='dynamic'))
    cmdline = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime(), default=datetime.now)
