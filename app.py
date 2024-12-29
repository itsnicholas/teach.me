"""Module information."""

from os import getenv
import secrets
from flask import Flask
from flask import redirect, render_template, request, session, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///xxxxxx" #getenv("DATABASE_URL") problem
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    """Function information."""
    sql = text("SELECT id, name FROM courses ORDER BY id;")
    result = db.session.execute(sql)
    courses = result.fetchall()
    return render_template("index.html", courses=courses)

@app.route("/login", methods=["POST"])
def login():
    """Function information."""
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
    """Function information."""
    del session["username"]
    return redirect("/")

@app.route("/signup")
def signup():
    """Function information."""
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup2():
    """Function information."""
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
                               " - kokeile toista käyttäjätunnusta")

    # store username and password
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users VALUES (DEFAULT, :username, :hash_value, false);")
    db.session.execute(sql, {"username":username, "hash_value":hash_value})
    db.session.commit()

    return redirect("/")

@app.route("/course/<int:course_id>")
def course(course_id):
    """Function information."""
    sql = text("SELECT id, name FROM courses WHERE id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    username_id = session["id"]
    sql = text("SELECT id FROM userscourses WHERE user_id=:username_id AND course_id=:course_id;")
    result = db.session.execute(sql, {"username_id":username_id, "course_id":course_id})
    join = result.fetchone()
    sql = text("SELECT id, material FROM materials WHERE course_id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    materials = result.fetchall()
    sql = text("SELECT id, question FROM textquestions WHERE course_id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    text_questions = result.fetchall()
    sql = text("SELECT id, question FROM multiplechoicequestions WHERE course_id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    multiple_choice_questions = result.fetchall()
    return render_template("course.html",
                           course_info=course_info, join=join, materials=materials,
                           text_questions=text_questions,
                           multiple_choice_questions = multiple_choice_questions)

@app.route("/course/<int:course_id>/text_question/<int:text_question_id>")
def multiple_choice(course_id, text_question_id):
    """Function information."""
    sql = text("SELECT id, course_id, question FROM textquestions WHERE" +
    " id=:text_question_id;")
    result = db.session.execute(sql, {"text_question_id":text_question_id})
    question = result.fetchone()
    print(question.question, "question.question")
    return render_template("text_question.html",
                           course_id=course_id, question=question)

@app.route("/course/<int:course_id>/multiple_choice/<int:multiple_choice_question_id>")
def text_question(course_id, multiple_choice_question_id):
    """Function information."""
    sql = text("SELECT id, option FROM multiplechoiceoptions WHERE" +
    " multiplechoicequestion_id=:multiple_choice_question_id;")
    result = db.session.execute(sql, {"multiple_choice_question_id":multiple_choice_question_id})
    choices = result.fetchall()
    sql = text("SELECT id, question FROM multiplechoicequestions WHERE" +
    " id=:multiple_choice_question_id;")
    result = db.session.execute(sql, {"multiple_choice_question_id":multiple_choice_question_id})
    question = result.fetchone()
    print(question.question, "question_text")
    return render_template("multiple_choice.html",
                           course_id=course_id, choices=choices,
                           question=question)

@app.route("/enrol", methods=["POST"])
def enrol():
    """Function information."""

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    user_id = session["id"]
    course_id = request.form["course_id"]
    sql = text("INSERT INTO userscourses VALUES (DEFAULT, :user_id, :course_id);")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/answer_text_question", methods=["POST"])
def answer_text_question():
    """Function information."""

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    text_question_answer = request.form["text_question_answer"]
    user_id = session["id"]
    task_id = request.form["task_id"]
    course_id = request.form["course_id"]

    sql = text("SELECT id, answer FROM textquestions WHERE id=:task_id;")
    result = db.session.execute(sql, {"task_id":task_id})
    text_question = result.fetchone()

    if text_question.answer != text_question_answer:
        flash('Väärä vastaus!')
        return redirect("/course/" + str(course_id)) #message="Väärä vastaus!")

    sql = text("SELECT id FROM userstasks WHERE user_id=:user_id AND " +
               "task_id=:task_id AND type=1;")
    result = db.session.execute(sql, {"user_id":user_id, "task_id":task_id})
    answer_already = result.fetchone()

    if answer_already:
        return redirect("/course/" + str(course_id)) #message="Vastasit jo oikein!")

    sql = text("INSERT INTO userstasks VALUES (DEFAULT, :user_id, :task_id, 1);")
    db.session.execute(sql, {"user_id":user_id, "task_id":task_id})
    db.session.commit()
    return redirect("/course/" + str(course_id)) #add error message e.g. ,
                                                #message="Oikea vastaus!!"?

@app.route("/answer_multiple_choice_question", methods=["POST"])
def answer_multiple_choice_question():
    """Function information."""

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    multiple_choice_question_answer = request.form["multiple_choice_question_answer"]
    user_id = session["id"]
    question_id = request.form["question_id"]
    course_id = request.form["course_id"]

    sql = text("SELECT id, answer FROM multiplechoicequestions WHERE id=:question_id;")
    result = db.session.execute(sql, {"question_id":question_id})
    multiple_choice_question = result.fetchone()

    print(multiple_choice_question.answer, "multiple_choice_question.answer")
    print(multiple_choice_question_answer, "multiple_choice_question_answer")

    if multiple_choice_question.answer != multiple_choice_question_answer:
        print("Väärä vastaus")
        flash('Väärä vastaus!')
        return redirect("/course/" + str(course_id)) #message="Väärä vastaus!")

    sql = text("SELECT id FROM userstasks WHERE user_id=:user_id AND " +
               "task_id=:task_id AND type=2;")
    result = db.session.execute(sql, {"user_id":user_id, "task_id":question_id})
    answer_already = result.fetchone()

    if answer_already:
        print("Vastasit jo oikein!")
        return redirect("/course/" + str(course_id)) #message="Vastasit jo oikein!")

    sql = text("INSERT INTO userstasks VALUES (DEFAULT, :user_id, :task_id, 2);")
    db.session.execute(sql, {"user_id":user_id, "task_id":question_id})
    db.session.commit()
    print("Oikea vastaus lisätty")
    return redirect("/course/" + str(course_id)) #add error message e.g. ,
                                                #message="Oikea vastaus!!"?
