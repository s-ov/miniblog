from flask import request
from urllib.parse import urlparse, urljoin
from config import Config
from app.extensions import db


def follow_user(current_user, user_to_follow):
    """Allow the current user to follow another user."""
    if not current_user.is_following(user_to_follow):
        current_user.followed.append(user_to_follow)
        db.session.commit()


def unfollow_user(current_user, user_to_unfollow):
    """Allow the current user to unfollow another user."""
    if current_user.is_following(user_to_unfollow):
        current_user.followed.remove(user_to_unfollow)
        db.session.commit()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https')\
           and ref_url.netloc == test_url.netloc


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]\
        .lower() in Config.ALLOWED_EXTENSIONS
