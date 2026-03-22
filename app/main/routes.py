from flask import render_template,flash,redirect,url_for,request,current_app,jsonify
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PasswordResetRequestForm,ResetPasswordForm,MessageForm
from app.email import send_password_reset_email
from app.models import User,Post,Message,Notification
from flask_login import current_user,login_user,logout_user,login_required
from urllib.parse import urlparse
from app import db
from datetime import datetime,timezone
from flask_babel import _
from app.main import bp
import sqlalchemy as sa
import threading
from app.tasks import example_task


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user=current_user
    page=request.args.get("page",1,type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=current_app.config["POSTS_PER_PAGE"],error_out=False)
    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(
    # page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    
    # ↓ この return の「位置（左側の空白の数）」が上の user= と同じことが重要です！
    return render_template('index.html', title='ホーム', posts=posts.items,next_url=next_url,prev_url=prev_url)#paginate() を使うと、データそのものだけでなく「次のページはあるか？」「全部で何ページあるか？」という便利な情報が詰まったオブジェクトが返ってきます。



@bp.route("/users")
def user_list():
    users=User.query.all()
    return render_template("user_list.html",title="ユーザー一覧",users=users)

@bp.route("/secret")
@login_required
def secret():
    return "ここは秘密のページです！"

@bp.route("/user/<username>")
@login_required
def user(username):
    user=current_user
    user=User.query.filter_by(username=username).first_or_404()
    posts=[
        {"author":user,"body":"テスト投稿 #1"},
        {"author":user,"body":"テスト投稿 #2"}
    ]
    return render_template("user.html",user=user,posts=posts)

@bp.route("/edit_profile",methods=["GET","POST"])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash("変更を保存しました")
        return redirect(url_for("main.edit_profile"))
    elif request.method=="GET":
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
    return render_template("edit_profile.html",title="プロフィール編集",form=form)

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()

@bp.route("/follow/<username>")
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("main.index"))
    if user==current_user:
        return redirect(url_for("main.index"))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for("main.user",username=username))

@bp.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for("main.user",username=username))

@bp.route("/send_message/<recipient>",methods=["GET","POST"])
@login_required
def send_message(recipient):
    user=db.first_or_404(sa.select(User).where(User.username==recipient))
    form=MessageForm()
    if form.validate_on_submit():
        msg=Message(author=current_user,recipient=user,body=form.body.data)
        db.session.add(msg)
        db.session.commit()
        user.add_notification("unread_message_count",user.new_messages())
        db.session.commit()
        flash("メッセージを送信しました。")
        return redirect(url_for("main.user",username=recipient))
    return render_template("send_message.html",title="Send Message",
                           form=form,recipient=recipient)

@bp.route('/notifications')
@login_required
def notifications():
    since=request.args.get('since',0.0,type=float)
    notifications=current_user.notifications.select().where(
        Notification.timestamp>since).order_by(Notification.timestamp.asc())
    return jsonify([{
        "name":n.name,
        "data":n.get_data(),
        "timestamp":n.timestamp
    }for n in db.session.scalars(notifications)])

@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time=datetime.now()
    current_user.add_notification("unread_message_count",0)
    db.session.commit()

    page=request.args.get("page",1,type=int)
    query=sa.select(Message).where(
        Message.recipient==current_user).order_by(Message.timestamp.desc())
    messages=db.paginate(query,page=page,per_page=10,error_out=False)

    return render_template("messages.html",messages=messages.items)

@bp.route("/export_posts")
def export_posts():
    #job=current_app.task_queue.enqueue("app.tasks.example_task",10)
    thread=threading.Thread(target=example_task,args=(10,))
    thread.start()
    flash("While working")
    return redirect(url_for('main.index'))







#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#venv\Scripts\activate