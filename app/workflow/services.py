from app.extensions import db
from app.posts.models import Post
from app.user.models import followers
from sqlalchemy.orm import aliased
from sqlalchemy import or_


def get_followed_posts(user):
    """Fetch posts only from users that the given user follows."""
    
    return Post.query.filter(
        or_(
            Post.user_id == user.id,  
            Post.user_id.in_(
                db.session.query(followers.c.followed_id).filter(followers.c.follower_id == user.id)
            )  
        )
    ).order_by(Post.timestamp.desc())
