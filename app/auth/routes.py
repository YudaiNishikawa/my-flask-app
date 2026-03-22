from flask import render_template, redirect, url_for, flash, request
from app import db
from app.auth import bp
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PasswordResetRequestForm,ResetPasswordForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from flask_babel import _
from urllib.parse import urlparse
from app.email import send_password_reset_email

@bp.route('/login', methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash(_("ユーザー名かパスワードが正しくありません"))
            return redirect(url_for("auth.login"))
        
        login_user(user,remember=form.remember_me.data)
        
        next_page=request.args.get("next")
        if not next_page or urlparse(next_page).netloc !="":
            next_page=url_for("main.index")
        return redirect(next_page)
    
    return render_template("login.html",title="サインイン",form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("おめでとうございます！ 登録が完了しました。")
        return redirect(url_for("auth.login"))

    return render_template("register.html", title="新規ユーザー登録", form=form)

@bp.route("/reset_password_request",methods=["GET","POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=PasswordResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instruction to reset your password")
        return redirect(url_for('auth.login'))
    return render_template("reset_password_request.html",title="Reset Password",form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html",form=form)
