from flask import render_template,flash,redirect,url_for,request
from app import app
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PasswordResetRequestForm,ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User,Post
from flask_login import current_user,login_user,logout_user,login_required
from urllib.parse import urlparse
from app import db
from datetime import datetime,timezone

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user=current_user
    page=request.args.get("page",1,type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=app.config["POSTS_PER_PAGE"],error_out=False)
    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(
    # page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    
    # ↓ この return の「位置（左側の空白の数）」が上の user= と同じことが重要です！
    return render_template('index.html', title='ホーム', posts=posts.items,next_url=next_url,prev_url=prev_url)#paginate() を使うと、データそのものだけでなく「次のページはあるか？」「全部で何ページあるか？」という便利な情報が詰まったオブジェクトが返ってきます。

@app.route('/login', methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("ユーザー名かパスワードが正しくありません")
            return redirect(url_for("login"))
        
        login_user(user,remember=form.remember_me.data)
        
        next_page=request.args.get("next")
        if not next_page or urlparse(next_page).netloc !="":
            next_page=url_for("index")
        return redirect(next_page)
    
    return render_template("login.html",title="サインイン",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("おめでとうございます！ 登録が完了しました。")
        return redirect(url_for("login"))

    return render_template("register.html", title="新規ユーザー登録", form=form)

@app.route("/users")
def user_list():
    users=User.query.all()
    return render_template("user_list.html",title="ユーザー一覧",users=users)

@app.route("/secret")
@login_required
def secret():
    return "ここは秘密のページです！"

@app.route("/user/<username>")
@login_required
def user(username):
    user=current_user
    user=User.query.filter_by(username=username).first_or_404()
    posts=[
        {"author":user,"body":"テスト投稿 #1"},
        {"author":user,"body":"テスト投稿 #2"}
    ]
    return render_template("user.html",user=user,posts=posts)

@app.route("/edit_profile",methods=["GET","POST"])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash("変更を保存しました")
        return redirect(url_for("edit_profile"))
    elif request.method=="GET":
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
    return render_template("edit_profile.html",title="プロフィール編集",form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()

@app.route("/follow/<username>")
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for("index"))
    if user==current_user:
        return redirect(url_for("index"))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for("user",username=username))

@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for("user",username=username))

@app.route("/reset_password_request",methods=["GET","POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=PasswordResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instruction to reset your password")
        return redirect(url_for('login'))
    return render_template("reset_password_request.html",title="Reset Password",form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset")
        return redirect(url_for("login"))
    return render_template("reset_password.html",form=form)

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#venv\Scripts\activate