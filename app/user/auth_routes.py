from flask import (
    Blueprint, render_template, redirect, url_for, flash, request
    )
from flask_login import (
    current_user, login_user, logout_user,
    )
from flask_babel import lazy_gettext as _

from app.extensions import db, mail
from app.user.models import User
from app.user.forms import (
    RegistrationForm, 
    LoginForm, 
    ResetPasswordRequestForm, 
    ResetPasswordForm
    )
from app.user.services import send_reset_email
from flask_mail import Mail, Message

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/test_email', methods=['GET', 'POST'])
def test_email():
    msg = Message("Дмитро Овсюк, привіт.", recipients=["s.ovsiuk@gmail.com"])
    msg.body = "This is a test."
    try:
        mail.send(msg)
        return "Test email sent successfully"
    except Exception as e:
        return f"Error: {e}"



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    "Register a new user"

    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data,
            )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('auth.login'))
    
    return render_template(
        'auth/register.html', 
        title='Реєстрація', 
        form=form,
        )


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    "Login current user"

    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Невірно ім\'я чи пароль')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('user.index'))

    return render_template(
        'auth/login.html', 
        title='Авторизація', 
        form=form,
        )


@auth_bp.route('/logout')
def logout():
    "Logout authorized user"
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Send request to receive email."""
    
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('No user with such email', 'warning')
            return redirect(url_for('auth.reset_password_request', _external=False))

        send_reset_email(user)
        flash('Перевірте свій email щодо інструкцій як змінити пароль', 'info')
        return redirect(url_for('auth.login'))
    else:
        print("❌ Form validation failed!")
        print(f"Form errors: {form.errors}")
        print(f"Email field errors: {form.email.errors}")
    return render_template(
        'auth/reset_password_request.html', 
        title='Змінити пароль', 
        form=form,
    )

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Allow users to reset their password using a valid token."""
    
    print(f"🔹 Received token: {token}")

    if not token:
        flash('Invalid or missing token.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user.index'))

    user = User.verify_reset_token(token)
    
    if user is None:
        flash('Invalid or expired token.', 'warning')
        print("❌ Token verification failed.")
        return redirect(url_for('auth.reset_password_request'))
    
    print(f"✅ Token valid for user: {user.email} (ID: {user.id})")

    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        print(f"🔹 Password successfully reset for {user.email}")
        return redirect(url_for('auth.login'))

    return render_template(
        'auth/reset_password.html', 
        form=form, 
        title='Reset Password',
        user=user,
    )


# @auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     """Allow users to reset their password using a valid token."""
#     if current_user.is_authenticated:
#         return redirect(url_for('user.index'))
        
#     user = User.verify_reset_token(token)
#     if not user:
#         flash('Invalid or expired token.', 'warning')
#         return redirect(url_for('auth.reset_password_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user.set_password(form.password.data)
#         db.session.commit()
#         flash('Your password has been reset.')
#         return redirect(url_for('auth.login'))
#     return render_template(
#         'auth/reset_password.html', form=form, title='Reset password',
#         )
