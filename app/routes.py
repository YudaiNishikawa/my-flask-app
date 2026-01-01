from flask import render_template
from app import app

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

