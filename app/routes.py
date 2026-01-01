from flask import render_template,flash,redirect,url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    # ユーザーのダミーデータ（本当はデータベースから取ってきますが、今は手動で）
    user = {'username': 'ユウダイ',"favorite_food": "えびフィレオ"}

    posts=[
        {
            "author":{"username":"ジョン"}
            ,"body":"今日は天気がいいね！"
        },
        {
            "author":{"username":"スーザン"},
            "body":"アベンジャーズの映画、最高だった！"
        },
        {
            "author":{"username":"yudai"},
            "body":"pythonの勉強中！"
        }
    ]
    
    return render_template('index.html', title='ホーム', user=user,posts=posts)

@app.route('/login', methods=["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        flash(f'ユーザー {form.username.data}のログイン要求を受け付けました（記憶する={form.remember_me.data}）')
        return redirect(url_for("index"))
    
    return render_template("login.html",title="サインイン",form=form)
