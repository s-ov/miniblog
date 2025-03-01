# from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import TimedSerializer as Serializer
import jwt
from app import db
from config import Config
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash, check_password_hash,
    )
from datetime import datetime
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers',
                     db.metadata,
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
                     extend_existing=True,
            )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    bio = db.Column(db.String(500))
    profile_picture = db.Column(db.String(255), nullable=True,)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.now())
    followed = db.relationship(
                    'User', secondary=followers,
                    primaryjoin=(followers.c.follower_id == id),
                    secondaryjoin=(followers.c.followed_id == id),
                    backref=db.backref('followers', lazy='dynamic'), 
                    lazy='dynamic',
                    )

    def __repr__(self):
        return f'<User: {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """Check if the current user follows another user."""
        if user is None:
            return False  
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def get_reset_token(self, expires_sec=600):
        """Generate a secure token for password reset (default: 5 minutes)."""
        serializer = Serializer(Config.SECRET_KEY, expires_sec)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        serializer = Serializer(Config.SECRET_KEY)
        try:
            user_id = serializer.loads(token)['user_id']
        except:
            return 
        return User.query.get(user_id)
    
    def get_reset_password_token(self, expires_in=600):
        """Generate a secure token for password reset (default: 5 minutes)."""
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.now() + expires_in},
            Config.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY,
                            algorithms=['HS256'])['reset_password']
        except:
            return 
        return db.session.get(User, id)
