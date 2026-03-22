from flask import jsonify
from app.api import bp
from app.models import User
from app import db
import sqlalchemy as sa

@bp.route("/users/<int:id>",methods=["GET"])
def get_user(id):
    user=db.get_or_404(User,id)
    return jsonify(user.to_dict())

@bp.route("/users",methods=["GET"])
def get_users():
    users=db.session.scalars(sa.select(User)).all()
    data=[u.to_dict() for u in dict]
    return jsonify(data)

@bp.route("/users/<int:id>/followers",methods=["GET"])
def get_followers(id):
    user=db.get_or_404(User,id)
    return jsonify({"items":[],"_links":{}})

@bp.route("/users/<int:id>/followed",methods=["GET"])
def get_following(id):
    user=db.get_or_404(User,id)
    return jsonify({"item":[],"_links":{}})