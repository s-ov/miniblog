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
