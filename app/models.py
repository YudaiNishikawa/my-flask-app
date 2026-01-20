from app import db,login
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime,timezone

followers=db.Table("followers",
    db.Column("follower_id",db.Integer,db.ForeignKey("user.id")),
    db.Column("followed_id",db.Integer,db.ForeignKey("user.id")))

class User(UserMixin,db.Model):
    
    id = db.Column(db.Integer,primary_key=True)

    username=db.Column(db.String(64),index=True,unique=True)

    email=db.Column(db.String(120),index=True,unique=True)

    followed=db.relationship(
        "User",secondary=followers,
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        backref=db.backref("followers",lazy="dynamic"),lazy="dynamic")

    password_hash=db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def avatar(self,size):
        digest=md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
    
    about_me=db.Column(db.String(140))
    last_seen=db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))