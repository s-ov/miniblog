from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    )
from flask_login import login_required, current_user
from config import Config
from app.extensions import db
from app.user.models import User
from app.posts.models import Post
from app.posts.forms import PostForm

workflow_bp = Blueprint(
    'workflow', __name__, template_folder='templates',
    )


@workflow_bp.route('/<username>', methods=['GET', 'POST'])
@login_required
def profile_page(username):
    "Display user profile along with their posts."
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')       # Post/Redirect/Get pattern
        return redirect(url_for('workflow.profile_page', username=current_user.username))
    
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc())\
                      .paginate(
                        page=page, 
                        per_page=Config.POSTS_PER_PAGE, 
                        error_out=False
                       )
    
    next_url = url_for(
        'workflow.profile_page', username=current_user.username, page=posts.next_num,
        ) \
    if posts.has_next else url_for(
        'workflow.profile_page', username=current_user.username, page=1,
        )
    prev_url = url_for(
        'workflow.profile_page', username=current_user.username, page=posts.prev_num,
        ) \
    if posts.has_prev else url_for(
        'workflow.profile_page', username=current_user.username, page=1,
        )


    return render_template(
        'workflow/profile_page.html',
        title='Profile page',
        form=form,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
    )


@workflow_bp.route('/chatroom/<username>', methods=['GET', 'POST'])
@login_required
def chatroom_page(username):
    """Display user profile along with their posts."""
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')       # Post/Redirect/Get pattern
        return redirect(url_for(
            'workflow.chatroom_page', 
            username=current_user.username,
            )
        )
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc())\
                      .paginate(
                        page=page, 
                        per_page=Config.POSTS_PER_PAGE, 
                        error_out=False
                       )
    next_url = url_for(
        'workflow.chatroom_page', page=posts.next_num, username=current_user.username,
        ) \
    if posts.has_next else url_for(
        'workflow.chatroom_page', username=current_user.username, page=1,
        )
    prev_url = url_for(
        'workflow.chatroom_page', page=posts.prev_num, username=current_user.username,
        ) \
    if posts.has_prev else url_for(
        'workflow.chatroom_page', username=current_user.username, page=1,
        )

    return render_template(
        'workflow/chatroom.html',
        title='Chatroom',
        form=form,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
    )
