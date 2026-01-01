from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username=StringField("ユーザー名",validators=[DataRequired()])
    password=PasswordField("パスワード",validators=[DataRequired()])
    remember_me=BooleanField("ログイン状態を保持する")
    submit=SubmitField("サインイン")