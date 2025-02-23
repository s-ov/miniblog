from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    )
from flask_login import login_required, current_user
from config import Config
from app.extensions import db
from app.user.models import User
from app.posts.models import Post
from app.posts.forms import PostForm
from app.workflow.models import follow_user, unfollow_user, get_followed_posts

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


@workflow_bp.route('/feed')
@login_required
def feed():
    """Display posts from followed users only."""
    posts = get_followed_posts(current_user).all()
    return render_template('workflow/feed.html', posts=posts)


@workflow_bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    """Follow a user by their ID."""
    user_to_follow = User.query.get_or_404(user_id)
    
    if user_to_follow == current_user:
        flash("You cannot follow yourself!", "warning")
        return redirect(url_for('user.profile', user_id=user_id))
    
    follow_user(current_user, user_to_follow)
    flash(f"You are now following {user_to_follow.username}!", "success")
    return redirect(url_for('user.profile', user_id=user_id))

@workflow_bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):
    """Unfollow a user by their ID."""
    user_to_unfollow = User.query.get_or_404(user_id)
    
    unfollow_user(current_user, user_to_unfollow)
    flash(f"You have unfollowed {user_to_unfollow.username}.", "info")
    return redirect(url_for('user.profile', user_id=user_id))
