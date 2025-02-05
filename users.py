import secrets
from db import db
from flask import session, flash
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    sql = text("SELECT id, password, admin FROM users WHERE username=:username;")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["id"] = user.id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            if user.admin:
                session["user"] = "admin"
            else:
                session["user"] = "student"
            return True
        return False

def logout():
    del session["username"]

def signup(username, password, admin):
    sql = text("SELECT id, password FROM users WHERE username=:username;")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if user:
        return False

    hash_value = generate_password_hash(password)

    try:
        sql = text("INSERT INTO users VALUES (DEFAULT, :username, :hash_value, :admin);")
        db.session.execute(sql, {"username":username, "hash_value":hash_value, "admin":admin})
        db.session.commit()
    except Exception:
        return False
    flash("Tili luotu!")
    return True

def get_user(username_id):
    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    user = result.fetchone()[1]
    return user

def get_user_session():
    return session["user"]

def user_id():
    return session["id"]

def session_token():
    return session["csrf_token"]
