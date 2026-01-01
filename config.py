import os

class Config(object):
    #　「秘密鍵の設定」
    # 環境変数に設定があればそれを使用し、なければ"you-will-never guess"を使用する
    SECRET_KEY=os.environ.get("SECRET_KEY") or "you-will-never-guess"