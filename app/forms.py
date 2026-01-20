from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from app.models import User

class LoginForm(FlaskForm):
    username=StringField("ユーザー名",validators=[DataRequired()])
    password=PasswordField("パスワード",validators=[DataRequired()])
    remember_me=BooleanField("ログイン状態を保持する")
    submit=SubmitField("サインイン")

class RegistrationForm(FlaskForm):
    username=StringField("ユーザー名",validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    password_confirm=PasswordField("パスワード（確認）",validators=[DataRequired(),EqualTo("password")])
    submit=SubmitField("登録")

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("そのユーザー名はすでに使われています。")
        
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("そのメールアドレスはすでに登録されています。")

class EditProfileForm(FlaskForm):
    username=StringField("ユーザー名",validators=[DataRequired()])
    about_me=TextAreaField("自己紹介",validators=[Length(min=0,max=140)])
    submit=SubmitField("保存")