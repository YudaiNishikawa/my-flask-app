from flask import Flask,request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import os
import logging
from logging.handlers import SMTPHandler,RotatingFileHandler
from flask_bootstrap import Bootstrap5
from flask_moment import Moment
from flask_babel import Babel,lazy_gettext as _l
import redis
#from rq import Queue

bootstrap = Bootstrap5()
moment=Moment()
babel=Babel()
import flask_bootstrap
bootstrap_template_path = os.path.join(os.path.dirname(flask_bootstrap.__file__), 'templates')
db=SQLAlchemy()
migrate=Migrate()
login=LoginManager()
login.login_view="auth.login"
mail=Mail()

def create_app(config_class=Config):
    app = Flask(__name__) # Flaskのおまじない
    app.config.from_object(config_class)
    app.register_blueprint(api_bp,url_prefix="/api")
    #app.redis=redis.from_url(app.config["REDIS_URL"])
    #app.task_queue=Queue("microblog-tasks",connection=app.redis)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app,locale_selector=get_locale)
    import flask_bootstrap
    bootstrap_template_path = os.path.join(os.path.dirname(flask_bootstrap.__file__), 'templates')
    app.jinja_loader.searchpath.append(bootstrap_template_path)
    db.init_app(app)
    migrate.init_app(app,db)
    login.init_app(app)
    mail.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp,url_prefix='/auth')
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug:
        if app.config["MAIL_SERVER"]:
            auth=None
            if app.config["MAIL_USERNAME"]or app.config["MAIL_PASSWORD"]:
                auth =(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure=()
            
            mail_handler=SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler=RotatingFileHandler("logs/microblog.log",maxBytes=10240,
                                            backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info("Microblog startup")

    return app

from flask import current_app
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from app.api import bp as api_bp
from app import models# 「ページ設定はroutes.pyを見てね」という意味
