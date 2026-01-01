from flask import Flask
from config import Config

app = Flask(__name__) # Flaskのおまじない
app.config.from_object(Config)

from app import routes # 「ページ設定はroutes.pyを見てね」という意味