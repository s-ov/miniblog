from flask import (
    Blueprint,
    render_template, 
    redirect, 
    flash,
    url_for,
    request,
    abort,
    )
from flask_login import (
    current_user, 
    logout_user,
    login_required,
    )

import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from datetime import datetime
from flask_babel import _
from config import Config
from app.extensions import db
from app.user.forms import (
    ResetPasswordRequestForm,
    ResetPasswordForm,
    EditProfileForm,
    EmptyForm,
    ProfilePictureForm,
    DeleteAccountForm,
    )
from app.user.models import User
from app.user.services import (
    allowed_file, 
    follow_user, 
    unfollow_user, 
    send_reset_email,
    )

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


@user_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_user_request():
    """Display confirmation form before deleting an account."""
    form = DeleteAccountForm()
    if current_user:
        if form.validate_on_submit():
            return redirect(url_for('user.delete_user')) 
    return render_template('user/delete_account.html', form=form)


@user_bp.route('/delete_account/confirm', methods=['POST'])
@login_required
def delete_user():
    """Verify password and delete user account."""
    form = DeleteAccountForm()
    
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.password.data):
            user_id = current_user.id
            logout_user()  
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash("Your account has been successfully deleted.", "success")
                return redirect(url_for('user.index')) 
        else:
            flash("Incorrect password. Account not deleted.", "danger")

    return redirect(url_for('user.delete_user_request'))  


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

    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.id != current_user.id)\
                    .order_by(User.username.desc())\
                    .paginate(
                        page=page, 
                        per_page=Config.USERS_PER_PAGE, 
                        error_out=False
                    )
    next_url = url_for(
        'user.get_users_list', username=current_user.username, page=users.next_num,
        ) \
    if users.has_next else url_for(
        'user.get_users_list', username=current_user.username, page=1,
        )
    prev_url = url_for(
        'user.get_users_list', username=current_user.username, page=users.prev_num,
        ) \
    if users.has_prev else url_for(
        'user.get_users_list', username=current_user.username, page=1,
        )


    return render_template(
        'user/users_list.html', 
        title='Users list',
        users=users,
        next_url=next_url,
        prev_url=prev_url,
    )


@user_bp.route('/get_user_profile/<username>', methods=['GET'])
@login_required
def get_user_profile(username):
    "Get a specific user's profile."

    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    return render_template(
        'user/user_profile.html', 
        title="User's profile",
        user=user,
    )


@user_bp.route('/follow/<username>', methods=['GET'])
@login_required
def follow(username):
    """Follow a user by their username."""
    user = User.query.filter_by(username=username).first_or_404()

    if user == current_user:
        flash("You cannot follow yourself!", "warning")
        return redirect(url_for('user.get_user_profile', username=username))
    
    follow_user(current_user, user)
    flash(f"You are now following {user.username}!", "success")
    return redirect(url_for('user.get_user_profile', username=username))

    
@user_bp.route('/unfollow/<username>', methods=['GET'])
@login_required
def unfollow(username):
    """Unfollow a user by their username."""
    user = User.query.filter_by(username=username).first_or_404()
    
    unfollow_user(current_user, user)
    flash(f"You have unfollowed {user.username}.", "info")
    return redirect(url_for('user.get_user_profile', username=username))
