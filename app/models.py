from app import db,login
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime,timezone
from flask import current_app,url_for#circular import を防ぐため
import jwt
from time import time
import sqlalchemy as sa
import sqlalchemy.orm as so
import json


followers=db.Table("followers",
    db.Column("follower_id",db.Integer,db.ForeignKey("user.id")),
    db.Column("followed_id",db.Integer,db.ForeignKey("user.id")))

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body=db.Column(db.String(140))
    timestamp=db.Column(db.DateTime,index=True,default=lambda:datetime.now(timezone.utc))
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Post {self.body}>"

class Notification(db.Model):
    id: so.Mapped[int]=so.mapped_column(primary_key=True)
    name: so.Mapped[str]=so.mapped_column(index=True)
    user_id: so.Mapped[int]=so.mapped_column(sa.ForeignKey("user.id"),index=True)
    timestamp: so.Mapped[float]=so.mapped_column(index=True,default=time)
    payload_json: so.Mapped[str]=so.mapped_column(sa.Text)
    user: so.Mapped["User"]=so.relationship("User",back_populates="notifications")

    def get_data(self):
        return json.loads(str(self.payload_json))


class Message(db.Model):
    id: so.Mapped[int]=so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int]=so.mapped_column(sa.ForeignKey("user.id"),index=True )
    recipient_id: so.Mapped[int]=so.mapped_column(sa.ForeignKey("user.id"),index=True)

    body: so.Mapped[str]=so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime]=so.mapped_column(index=True,default=lambda:datetime.now(timezone.utc))
    author: so.Mapped["User"]=so.relationship(
        "User",
        back_populates="messages_sent",
        foreign_keys=[sender_id]
    )
    recipient: so.Mapped["User"]=so.relationship(
        "User",
        back_populates="message_received",
        foreign_keys=[recipient_id]
    )

class User(UserMixin,db.Model):
    __tablename__="user"
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),index=True,unique=True)
    email=db.Column(db.String(120),index=True,unique=True)
    followed=db.relationship(
        "User",secondary=followers,
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        backref=db.backref("followers",lazy="dynamic"),lazy="dynamic")
    password_hash=db.Column(db.String(128))
    posts=db.relationship("Post",backref="author",lazy="dynamic")
    about_me=db.Column(db.String(140))
    last_seen=db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))
    last_message_read_time: so.Mapped[datetime | None] = so.mapped_column(
        default=None)
    
    messages_sent: so.WriteOnlyMapped["Message"]=so.relationship(
        "Message",
        back_populates="author",
        foreign_keys="Message.sender_id"
    )
    message_received: so.WriteOnlyMapped["Message"]=so.relationship(
        "Message",
        back_populates="recipient",
        foreign_keys="Message.recipient_id"
    )

    notifications: so.WriteOnlyMapped["Notification"]=so.relationship("Notification",back_populates="user")

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def avatar(self,size):
        digest=md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
    
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        return self.followed.filter(
            followers.c.followed_id==user.id).count()>0
    
    def followed_posts(self):
        followed = Post.query.join(
        followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
    # unionを使って「フォロー中」と「自分」を合体させる
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def get_reset_password_token(self,expires_in=600):
        # 10分間（600秒）だけ有効な「合言葉」を作成
        return jwt.encode(
            {"reset_password":self.id, "exp":time()+expires_in},
            current_app.config["SECRET_KEY"],algorithm="HS256")
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token,current_app.config["SECRET_KEY"],
                          algorithms=["HS256"])["reset_password"]
        except:
            return None
        return User.query.get(id)
    
    def add_notification(self,name,data):
        n=db.session.scalar(
            self.notifications.select().where(Notification.name==name)
        )
        pay_load=json.dumps(data)
        
        if n:
            n.payload_json=pay_load
            n.timestamp=time()
        else:
            n=Notification(name=name,payload_json=pay_load,user=self,timestamp=time())
            db.session.add(n)
        return n
    
    def new_messages(self):
        return db.session.scalar(sa.select(sa.func.count(Message.id)).where(
            Message.recipient==self,
            Message.timestamp>(self.last_message_read_time or datetime(1900,1,1))
        ))
    
    def to_dict(self,include_email=False):
        data={
            "id": self.id,
            "username": self.username,
            "last_seen": self.last_seen.isoformat() + "Z" if self.last_seen else None,
            "about_me": self.about_me,
            "post_count": db.session.scalar(sa.select(sa.func.count(Post.id)).where(Post.user_id == self.id)),
            "follower_count": db.session.scalar(sa.select(sa.func.count()).select_from(followers).where(followers.c.followed_id == self.id)),
            "following_count": db.session.scalar(sa.select(sa.func.count()).select_from(followers).where(followers.c.follower_id == self.id)),
            "_links": {
                "self": url_for('api.get_user',id=self.id),
                "followers": url_for("api.get_followers",id=self.id),
                "followed": url_for("api.get_following", id=self.id),
                "avatar": self.avatar(128)
            }
        }
        if include_email:
            data["email"]=self.email
        return data
    
    def from_dict(self,data,new_user=False):
        for field in ["username","email","about_me"]:
            if field in data:
                setattr(self,field,data[field])
        if new_user and "password" in data:
            self.set_password(data["password"])

@login.user_loader
def load_user(id):
    return User.query.get(int(id))





    


    

    
