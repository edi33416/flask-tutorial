from datetime import datetime
from app import db, login

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from hashlib import md5

"""
Association table used by many-to-many relationship between Users
"""
followers = db.Table("followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    """
    user.posts will retrieve all the Posts made by this User
    post.author will retrieve the User that made the Post
    """
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)

    """
    Define many-to-many relationship between User instances.
    user1 = user2 has the meaning of: user1 is following user2
        * secondary = sets association table defined above
        * primaryjoin = links follower with association table
        * secondaryjoin = links followed with association table
    """
    followed = db.relationship(
        "User", secondary = followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy = "dynamic"), lazy = "dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        # Get Gravatar
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        # Get posts from followed users
        posts_followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id))\
                                   .filter(followers.c.follower_id == self.id)

        # A user expects to find his own posts in his timeline
        posts_owned = Post.query.filter_by(user_id == self.id)

        # Create a union of the posts, ordered by the most recent one
        return posts_followed.union(posts_owned).order_by(Post.timestamp.desc())

    def __repr__(self):
        return "<User {}>".format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {}>".format(self.body)
