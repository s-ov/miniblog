from flask import (
    Blueprint, render_template, redirect, request, url_for, flash,
    )
from flask_login import current_user, login_required
from config import Config
from app.extensions import db
from app.posts.models import Post
from app.posts.forms import PostForm

posts_bp = Blueprint(
    "posts", __name__, template_folder="templates",
    )


@posts_bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    "Create a post instance"
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('user.index'))       # Post/Redirect/Get pattern

    posts = Post.query.all()
    
    return render_template(
            'posts/create_post.html', 
            title='Create post', 
            form=form,
            posts=posts,
        )


@posts_bp.route("/delete_post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    """Deletes a Post instance by ID."""
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("You are not authorized to delete this post.", "danger")
        return redirect(url_for("posts.get_all_posts"))

    db.session.delete(post)
    db.session.commit()
    
    flash("Post deleted successfully.", "success")
    return redirect(url_for("posts.get_all_posts"))


@posts_bp.route('/all_posts')
@login_required
def get_all_posts():
    "Display all users' posts."
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc())\
                      .paginate(
                        page=page, 
                        per_page=Config.POSTS_PER_PAGE, 
                        error_out=False
                       )
    next_url = url_for('posts.get_all_posts', page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('posts.get_all_posts', page=posts.prev_num) \
    if posts.has_prev else None

    return render_template(
        "posts/index.html", 
        title='All posts', 
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
        )
