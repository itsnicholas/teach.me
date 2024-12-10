from flask import Flask
from flask import redirect, render_template, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    sql = text("SELECT id, name FROM courses ORDER BY id;")
    result = db.session.execute(sql)
    courses = result.fetchall()
    return render_template("index.html", courses=courses)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) > 16:
        return render_template("index.html", error="Tunnus on liian pitkä")
    if len(username) < 1:
        return render_template("index.html", error="Tunnus on liian lyhyt")
    if len(password) > 16:
        return render_template("index.html", error="Salasana on liian pitkä")
    if len(password) < 8:
        return render_template("index.html", error="Salasana on liian lyhyt")

    sql = text("SELECT id, password FROM users WHERE username =:username;")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if not user:
        # invalid username
        return render_template("index.html", message="Käyttäjätunnus on väärä")
    else:
        hash_value = user.password
        # correct username and password
        if check_password_hash(hash_value, password):
            session["id"] = user.id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")

        # invalid password
        return render_template("index.html", message="Salasana on väärä")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup2():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) > 16:
        return render_template("signup.html", error="Tunnus on liian pitkä")
    if len(username) < 1:
        return render_template("signup.html", error="Tunnus on liian lyhyt")
    if len(password) > 16:
        return render_template("signup.html", error="Salasana on liian pitkä")
    if len(password) < 8:
        return render_template("signup.html", error="Salasana on liian lyhyt")

    sql = text("SELECT id, password FROM users WHERE username =:username;")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if user:
        return render_template("signup.html", message="Käyttäjätunnus on käytössä" +
                               " - kokeile toista käyttäjätunnettu järkevästi osiin moduuleiksi ja funktioiksiusta")

    # store username and password
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users VALUES (DEFAULT, :username, :hash_value, false);")
    db.session.execute(sql, {"username":username, "hash_value":hash_value})
    db.session.commit()

    return redirect("/")

@app.route("/course/<int:id>")
def course(id):
    sql = text("SELECT name FROM courses WHERE id=:id;")
    result = db.session.execute(sql, {"id":id})
    name = result.fetchone()[0]
    username_id = session["id"]
    sql = text("SELECT id FROM userscourses WHERE user_id=:username_id AND course_id=:id;")
    result = db.session.execute(sql, {"username_id":username_id, "id":id})
    join = result.fetchone()
    sql = text("SELECT id, material FROM materials WHERE course_id=:id;")
    result = db.session.execute(sql, {"id":id})
    materials = result.fetchall()
    return render_template("course.html", id=id, name=name, join=join, materials=materials)

@app.route("/enrol", methods=["POST"])
def enrol():

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    user_id = session["id"]
    course_id = request.form["id"]
    sql = text("INSERT INTO userscourses VALUES (DEFAULT, :user_id, :course_id);")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))
