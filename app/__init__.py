from flask import Flask

app = Flask(__name__) # Flaskのおまじない

from app import routes # 「ページ設定はroutes.pyを見てね」という意味