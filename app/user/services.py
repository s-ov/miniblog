from flask import request, url_for
from flask_mail import Message
from urllib.parse import urlparse, urljoin
from config import Config
from app.extensions import db, mail


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


def send_reset_email(user):
    """Sends a password reset email to the user."""
    token = user.get_reset_token()  
    reset_link = url_for('user.reset_password', token=token, _external=True)

    msg = Message(
        'Password Reset Request',
        sender='noreply@gmail.com',
        recipients=[user.email]
    )
    msg.body = f''' To reset your password, visit the following link:
                    {reset_link}
                    If you did not make this request, simply ignore this email. 
                    This link will expire in 30 minutes.
                '''
    mail.send(msg)
