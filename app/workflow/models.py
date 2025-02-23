from app.extensions import db
from app.posts.models import Post
from app.user.models import followers


def get_followed_posts(user):
    """Fetch posts only from users that the given user follows."""
    return Post.query.join(
                        followers, 
                        (followers.c.followed_id == Post.user_id),
                    ).filter(
                        followers.c.follower_id == user.id
                    ).order_by(Post.timestamp.desc())


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
