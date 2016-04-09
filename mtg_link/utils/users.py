from passlib.hash import sha256_crypt
from mtg_link import db
from mtg_link.models.users import User
from mtg_link.models.sessions import Session
from datetime import datetime, timedelta
from uuid import uuid4
from flask import request

def is_valid_login(username, password):
    user = User.filter_by(username=username).first()
    if user:
        return sha256_crypt.verify(password, user.password)
    else:
        return False

def login(username, password):
    if is_valid_login(username, password):
        user = User.filter_by(username=username).first()
        active_sessions = Session.filter_by(active=True, user_id=user.id).all()
        if active_sessions:
            for sess in active_sessions:
                sess.active = False
        session = Session()
        session.user_id = user.id
        session.create_date = datetime.now()
        session.expire_date = datetime.now() + timedelta(days=30)
        session.token = uuid4()
        session.insert()
        db.Session.commit()
        return session
    else:
        return None

def get_active_user():
    if 'sessionId' in request.cookies:
        sess = Session.get(request.cookies.get('sessionId'))
        if sess and sess.active:
            return User.get(sess.user_id)
        else:
            return None
    else:
        return None
