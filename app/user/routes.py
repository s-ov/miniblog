from flask import (
    Blueprint,
    render_template, 
    redirect, 
    flash,
    url_for,
    request,
    )
from flask_login import (
    current_user, 
    login_user, 
    logout_user,
    login_required,
    )

import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_babel import _
from config import Config
from app.extensions import db
from app.user.forms import (
    LoginForm, 
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    EditProfileForm,
    EmptyForm,
    ProfilePictureForm,
    )
from app.user.models import User
# from app.email import send_email
from app.user.services import allowed_file

user_bp = Blueprint(
    'user',
    __name__, 
    template_folder='templates',
    )
    

@user_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@user_bp.route('/')
def index():
    "Render index page"
    return render_template(
        'user/index.html', 
        title='Index page',
        )


@user_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('user.login'))
    
    return render_template(
        'user/register.html', 
        title='Реєстрація', 
        form=form,
        )


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    "Login current user"

    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Невірно ім\'я чи пароль')
            return redirect(url_for('user.login'))
        
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('user.index'))

    return render_template(
        'user/login.html', 
        title='Авторизація', 
        form=form,
        )


@user_bp.route('/logout')
def logout():
    "Logout authorized user"
    
    logout_user()
    return redirect(url_for('user.login'))


@user_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if user:
        #     send_password_reset_email(user)
        flash('Перевірте свій email щодо інструкцій як змінити пароль')
        return redirect(url_for('user.login'))
    return render_template('user/reset_password_request.html',
                            title='Змінити пароль', 
                            form=form,
                            )


@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('user.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль змінено успішно.')
        return redirect(url_for('user.login'))
    return render_template(
        'user/reset_password.html', 
        title="Змінити пароль", 
        form=form,
        )


@user_bp.route('/upload/<int:user_id>', methods=['GET', 'POST'])
def upload_profile_picture(user_id):
    "Upload profile picture"
    user = User.query.get_or_404(user_id)
    form = ProfilePictureForm()

    if form.validate_on_submit():
        file = form.profile_picture.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(file_path)

            user.profile_picture = filename
            db.session.commit()
            flash('Profile picture updated!', 'success')
            return redirect(url_for('user.index',))

    return render_template(
        'user/upload_photo.html', 
        title='Upload photo',
        form=form, 
        user=user,
        )


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    "Handle user profile page updating"
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Зміни були збережені.')
        return redirect(url_for('user.edit_profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    return render_template(
        'user/edit_profile.html', 
        title='Редагувати профіль',
        form=form,
        )


@user_bp.route('/all_users', methods=['GET'])
@login_required
def get_users_list():
    "Get a list of all users."
    users = User.query.all()

    return render_template(
        'user/users_list.html', 
        title='Users list',
        users=users,
    )


@user_bp.route('/get_user/<username>', methods=['GET'])
@login_required
def get_user(username):
    "Get a specific user's profile."

    user = User.query.filter_by(username=username).first()

    return render_template(
        'user/users_list.html', 
        title="User's profile",
        user=user,
    )


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    "Handle follow user action"
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_(f'User {username} not found.'))
            return redirect(url_for('user.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user.user_profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user.user_profile', username=username))
    else:
        return redirect(url_for('user.index'))
    

@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    "Handle unfollow user action"
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('user.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user.user_profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user.user_profile', username=username))
    else:
        return redirect(url_for('user.index'))
