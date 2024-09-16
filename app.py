from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    result = db.session.execute(text("SELECT id, password FROM users WHERE username = '" +
                                     username + "';"))
    user = result.fetchone()

    if not user:
        # invalid username
        return redirect("/", message="Väärä käyttäjätunnus")
    else:
        # correct username and password
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            return redirect("/")
        else:
            # invalid password
            return redirect("/", message="Väärä salasana")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

#@app.route("/signup")
#def signup():
#    return render_template("signup.html")

#@app.route("/signup2", methods=["POST"])
#def signup2():
#    username = request.form["username"]
#    password = request.form["password"]
#    return redirect("/")
