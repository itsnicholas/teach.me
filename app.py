from os import getenv
from flask import Flask
import secrets
from flask import redirect, render_template, request, session, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if len(username) > 16:
        return render_template("index.html", message="Tunnus on liian pitkä")
    if len(username) < 1:
        return render_template("index.html", message="Tunnus on liian lyhyt")
    if len(password) > 16:
        return render_template("index.html", message="Salasana on liian pitkä")
    if len(password) < 8:
        return render_template("index.html", message="Salasana on liian lyhyt")

    sql = text("SELECT id, password, admin FROM users WHERE username=:username;")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()

    if not user:
        return render_template("index.html", message="Käyttäjätunnus on väärä")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["id"] = user.id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            if user.admin:
                session["user"] = "admin"
            else:
                session["user"] = "student"
            return redirect("/courses")
        return render_template("index.html", message="Salasana on väärä")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(username) > 16:
            return render_template("signup.html", message="Tunnus on liian pitkä")
        if len(username) < 1:
            return render_template("signup.html", message="Tunnus on liian lyhyt")
        if len(password) > 16:
            return render_template("signup.html", message="Salasana on liian pitkä")
        if len(password) < 8:
            return render_template("signup.html", message="Salasana on liian lyhyt")

        sql = text("SELECT id, password FROM users WHERE username=:username;")
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()

        if user:
            return render_template("signup.html", message="Käyttäjätunnus on käytössä" +
                                " - kokeile toista käyttäjätunnusta")

        hash_value = generate_password_hash(password)
        sql = text("INSERT INTO users VALUES (DEFAULT, :username, :hash_value, false);")
        db.session.execute(sql, {"username":username, "hash_value":hash_value})
        db.session.commit()
        return redirect("/")

@app.route("/courses")
def courses():
    username_id = session["id"]

    sql = text("SELECT id, name FROM courses WHERE visible=True ORDER BY id;")
    result = db.session.execute(sql)
    courses_info = result.fetchall()
    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    admin = result.fetchone()[1]
    return render_template("courses.html", courses_info=courses_info, admin=admin)

@app.route("/add_course", methods=["POST"])
def add_course():
    course_name = request.form["course_name"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(course_name) > 50:
        return render_template("error.html", message="Kurssin nimi on liian pitkä")
    if len(course_name) < 1:
        return render_template("error.html", message="Kurssin nimi on liian lyhyt")

    sql = text("SELECT id FROM courses WHERE name=:course_name AND visible=True;")
    result = db.session.execute(sql, {"course_name":course_name})
    course_result = result.fetchone()

    if not course_result:
        sql = text("INSERT INTO courses VALUES (DEFAULT, :course_name, DEFAULT);")
        db.session.execute(sql, {"course_name":course_name})
        db.session.commit()
    return redirect("/courses")

@app.route("/remove_course", methods=["POST"])
def remove_course():
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    sql = text("UPDATE courses SET visible=False WHERE id=:course_id AND visible=True;")
    db.session.execute(sql, {"course_id":course_id})
    db.session.commit()
    return redirect("/courses")

@app.route("/course/<int:course_id>")
def course(course_id):
    username_id = session["id"]

    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    admin = result.fetchone()[1]
    sql = text("SELECT id, name FROM courses WHERE id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    sql = text("SELECT id FROM userscourses WHERE user_id=:username_id AND course_id=:course_id;")
    result = db.session.execute(sql, {"username_id":username_id, "course_id":course_id})
    join = result.fetchone()
    sql = text("SELECT id, material FROM materials WHERE course_id=:course_id AND visible=True " +
               "ORDER BY id ASC;")
    result = db.session.execute(sql, {"course_id":course_id})
    materials = result.fetchall()
    sql = text("SELECT id, question FROM textquestions WHERE course_id=:course_id AND " +
               "visible=True ORDER BY id;")
    result = db.session.execute(sql, {"course_id":course_id})
    text_questions = result.fetchall()
    sql = text("SELECT id, question FROM multiplechoicequestions WHERE course_id=:course_id AND " +
               "visible=True ORDER BY id;")
    result = db.session.execute(sql, {"course_id":course_id})
    mc_questions = result.fetchall()
    sql = text("SELECT t.question FROM textquestions t, usersquestions u WHERE t.id=u.question_id" +
               " AND u.course_id=:course_id AND u.user_id=:user_id AND u.type=1 AND " +
               "t.visible=True ORDER BY t.id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":username_id})
    tq_answers = result.fetchall()
    sql = text("SELECT m.question FROM multiplechoicequestions m, usersquestions u " +
               "WHERE m.id=u.question_id AND u.course_id=:course_id AND u.user_id=:user_id AND " +
               "u.type=2 AND m.visible=True ORDER BY m.id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":username_id})
    mcq_answers = result.fetchall()
    sql = text("SELECT u.id, u.username FROM users u, userscourses o, courses c " +
               "WHERE u.id=o.user_id AND o.course_id=c.id AND c.name=:course_name;")
    result = db.session.execute(sql, {"course_name":course_info.name})
    course_enrolled = result.fetchall()
    return render_template("course.html",
                           course_info=course_info, join=join, materials=materials,
                           text_questions=text_questions, tq_total=
                           len(text_questions),
                           tq_answers=tq_answers,
                           tq_answers_total=len(tq_answers),
                           mc_questions=mc_questions,
                           mcq_total=len(mc_questions),
                           mcq_answers=mcq_answers,
                           mcq_answers_total=len(mcq_answers),
                           course_enrolled=course_enrolled, admin=admin)

@app.route("/change_ct", methods=["POST"])
def change_ct():
    course_title = request.form["course_title"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(course_title) > 50:
        return render_template("error.html", message="Kurssin nimi on liian pitkä")
    if len(course_title) < 1:
        return render_template("error.html", message="Kurssin nimi on liian lyhyt")

    sql = text("UPDATE courses SET name=:course_title WHERE id=:course_id;")
    db.session.execute(sql, {"course_title":course_title, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/enrol", methods=["POST"])
def enrol():
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "student":
        abort(403)

    user_id = session["id"]
    course_id = request.form["course_id"]
    sql = text("INSERT INTO userscourses VALUES (DEFAULT, :user_id, :course_id);")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/remove_material", methods=["POST"])
def remove_material():
    course_id = request.form["course_id"]
    material_id = request.form["material_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    sql = text("UPDATE materials SET visible=False WHERE id=:material_id AND course_id=:course_id;")
    db.session.execute(sql, {"material_id": material_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/add_material", methods=["POST"])
def add_material():
    material_answer = request.form["material_answer"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(material_answer) > 500:
        return render_template("error.html", message="Materiaali on liian pitkä")
    if len(material_answer) < 1:
        return render_template("error.html", message="Materiaali on liian lyhyt")

    sql = text("INSERT INTO materials VALUES (DEFAULT, :course_id, :material_answer, DEFAULT);")
    db.session.execute(sql, {"course_id":course_id, "material_answer":material_answer})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/material/<int:material_id>")
def material(course_id, material_id):
    username_id = session["id"]

    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    admin = result.fetchone()[1]
    sql = text("SELECT id, material FROM materials WHERE id=:material_id AND course_id=:course_id;")
    result = db.session.execute(sql, {"material_id":material_id, "course_id":course_id})
    material_text = result.fetchone()[1]
    return render_template("material.html", material_id=material_id, course_id=course_id,
                           material_text=material_text, admin=admin)

@app.route("/change_material", methods=["POST"])
def change_material():
    course_id = request.form["course_id"]
    material_id = request.form["material_id"]
    material_text = request.form["material_text"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(material_text) > 500:
        return render_template("error.html", message="Materiaali on liian pitkä")
    if len(material_text) < 1:
        return render_template("error.html", message="Materiaali on liian lyhyt")

    sql = text("UPDATE materials SET material=:material_text WHERE id=:material_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"material_id": material_id, "course_id":course_id,
                             "material_text":material_text})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/remove_tq", methods=["POST"])
def remove_tq():
    course_id = request.form["course_id"]
    tq_id = request.form["tq_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    sql = text("UPDATE textquestions SET visible=False WHERE id=:tq_id " +
               "AND course_id=:course_id;")
    db.session.execute(sql, {"tq_id": tq_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/add_tq", methods=["POST"])
def add_tq():
    question = request.form["question"]
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(question) > 100:
        return render_template("error.html", message="Kysymys on liian pitkä")
    if len(question) < 1:
        return render_template("error.html", message="Kysymys on liian lyhyt")
    if len(answer) > 200:
        return render_template("error.html", message="Vastaus on liian pitkä")
    if len(answer) < 1:
        return render_template("error.html", message="Vastaus on liian lyhyt")

    sql = text("INSERT INTO textquestions VALUES (DEFAULT, :course_id, :question, " +
               ":answer, DEFAULT);")
    db.session.execute(sql, {"course_id":course_id, "question":question, "answer":answer})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/add_mcq", methods=["POST"])
def add_mcq():
    question = request.form["question"]
    choices = request.form.getlist("choice")
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(question) > 100:
        return render_template("error.html", message="Kysymys on liian pitkä")
    if len(question) < 1:
        return render_template("error.html", message="Kysymys on liian lyhyt")

    for choice in choices:
        if len(choice) > 50:
            return render_template("error.html", message="Vastaus on liian pitkä")
        if len(choice) < 1:
            return render_template("error.html", message="Vastaus on liian lyhyt")

    sql = text("INSERT INTO multiplechoicequestions VALUES (DEFAULT, " +
               ":course_id, :answer, :question, DEFAULT) RETURNING id;")
    result = db.session.execute(sql, {"course_id":course_id, "answer":choices[int(answer)-1],
                                      "question":question})
    db.session.commit()
    last_inserted_id = result.fetchone()[0]

    for choice in choices:
        if choice != "":
            sql = text("INSERT INTO multiplechoiceoptions VALUES (DEFAULT, :id, :choice)")
            db.session.execute(sql, {"id":last_inserted_id, "choice":choice})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/remove_mcq", methods=["POST"])
def remove_mcq():
    course_id = request.form["course_id"]
    mcq_id = request.form["mcq_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    sql = text("UPDATE multiplechoicequestions SET visible=False WHERE id=:mcq_id " +
               "AND course_id=:course_id;")
    db.session.execute(sql, {"mcq_id": mcq_id, "course_id":course_id})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/enrolled/<int:student_id>")
def enrolled(course_id, student_id):
    sql = text("SELECT id, name FROM courses WHERE id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    sql = text("SELECT id, username FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":student_id})
    student = result.fetchone()
    sql = text("SELECT id, question FROM textquestions WHERE course_id=:course_id AND " +
               "visible=True;")
    result = db.session.execute(sql, {"course_id":course_id})
    text_questions = result.fetchall()
    sql = text("SELECT id, question FROM multiplechoicequestions WHERE course_id=:course_id AND " +
               "visible=True;")
    result = db.session.execute(sql, {"course_id":course_id})
    mc_questions = result.fetchall()
    sql = text("SELECT t.question FROM textquestions t, usersquestions u " +
               "WHERE t.id=u.question_id AND u.course_id=:course_id AND u.user_id=:user_id AND " +
               "u.type=1 AND t.visible=True;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":student_id})
    tq_answers = result.fetchall()
    sql = text("SELECT m.question FROM multiplechoicequestions m, usersquestions u " +
               "WHERE m.id=u.question_id AND u.course_id=:course_id AND u.user_id=:user_id AND " +
               "u.type=2 AND m.visible=True")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":student_id})
    mcq_answers = result.fetchall()
    return render_template("enrolled.html", course_info=course_info,
                           text_questions=text_questions, student=student,
                           tq_total=len(text_questions),
                           tq_answers=tq_answers,
                           tq_answers_total=len(tq_answers),
                           mc_questions=mc_questions,
                           mcq_total=len(mc_questions),
                           mcq_answers=mcq_answers,
                           mcq_answers_total=len(mcq_answers))

@app.route("/course/<int:course_id>/text_question/<int:text_question_id>")
def multiple_choice(course_id, text_question_id):
    username_id = session["id"]

    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    admin = result.fetchone()[1]
    sql = text("SELECT id, course_id, answer, question FROM textquestions WHERE" +
               " id=:text_question_id AND visible=True;")
    result = db.session.execute(sql, {"text_question_id":text_question_id})
    question = result.fetchone()
    return render_template("text_question.html",
                           course_id=course_id, question=question, admin=admin)

@app.route("/change_tq_title", methods=["POST"])
def change_tq_title():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    tq_title = request.form["tq_title"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(tq_title) > 100:
        return render_template("error.html", message="Kysymys on liian pitkä")
    if len(tq_title) < 1:
        return render_template("error.html", message="Kysymys on liian lyhyt")

    sql = text("UPDATE textquestions SET question=:tq_title WHERE id=:question_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "tq_title":tq_title})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/change_tq_answer", methods=["POST"])
def change_tq_answer():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    tq_answer = request.form["tq_answer"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(tq_answer) > 200:
        return render_template("error.html", message="Vastaus on liian pitkä")
    if len(tq_answer) < 1:
        return render_template("error.html", message="Vastaus on liian lyhyt")

    sql = text("UPDATE textquestions SET answer=:tq_answer WHERE id=:question_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "tq_answer":tq_answer})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/multiple_choice/<int:mcq_id>")
def text_question(course_id, mcq_id):
    username_id = session["id"]

    sql = text("SELECT id, admin FROM users WHERE id=:username_id;")
    result = db.session.execute(sql, {"username_id":username_id})
    admin = result.fetchone()[1]
    sql = text("SELECT id, option FROM multiplechoiceoptions WHERE " +
               "multiplechoicequestion_id=:mcq_id;")
    result = db.session.execute(sql, {"mcq_id":mcq_id})
    choices = result.fetchall()
    sql = text("SELECT id, question, answer FROM multiplechoicequestions WHERE " +
               "id=:mcq_id AND visible=True;")
    result = db.session.execute(sql, {"mcq_id":mcq_id})
    question = result.fetchone()
    return render_template("multiple_choice.html",
                           course_id=course_id, choices=choices,
                           question=question, admin=admin)

@app.route("/change_mcq_title", methods=["POST"])
def change_mcq_title():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    mcq_title = request.form["mcq_title"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    if len(mcq_title) > 100:
        return render_template("error.html", message="Kysymys on liian pitkä")
    if len(mcq_title) < 1:
        return render_template("error.html", message="Kysymys on liian lyhyt")

    sql = text("UPDATE multiplechoicequestions SET question=:mcq_title " +
               "WHERE id=:question_id AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "mcq_title":mcq_title})
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/change_mcq_answer", methods=["POST"])
def change_mcq_answer():
    choices = request.form.getlist("choice")
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "admin":
        abort(403)

    for choice in choices:
        if len(choice) > 50:
            return render_template("error.html", message="Vastaus on liian pitkä")
        if len(choice) < 1:
            return render_template("error.html", message="Vastaus on liian lyhyt")

    sql = text("UPDATE multiplechoicequestions SET answer=:answer " +
               "WHERE id=:question_id AND course_id=:course_id;")
    db.session.execute(sql, {"course_id":course_id, "answer":choices[int(answer)-1],
                                      "question_id":question_id})
    db.session.commit()
    sql = text("SELECT id, option FROM multiplechoiceoptions WHERE " +
               "multiplechoicequestion_id=:question_id;")
    result = db.session.execute(sql, {"question_id":question_id})
    options = result.fetchall()

    i = 0
    for option in options:
        sql = text("UPDATE multiplechoiceoptions SET option=:choice " +
                   "WHERE id=:option_id")
        db.session.execute(sql, {"option_id":option.id, "choice":choices[i]})
        i += 1
    db.session.commit()
    return redirect("/course/" + str(course_id))

@app.route("/answer_tq", methods=["POST"])
def answer_tq():
    tq_answer = request.form["tq_answer"]
    user_id = session["id"]
    question_id = request.form["question_id"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "student":
        abort(403)

    if len(tq_answer) > 200:
        return render_template("error.html", message="Vastaus on liian pitkä")
    if len(tq_answer) < 1:
        return render_template("error.html", message="Vastaus on liian lyhyt")

    sql = text("SELECT id FROM usersquestions WHERE course_id=:course_id AND " +
               "user_id=:user_id AND type=1 AND question_id=:question_id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                                      "question_id":question_id})
    answer_already = result.fetchone()

    if answer_already:
        flash("Vastasit jo oikein!")
        return redirect("/course/" + str(course_id))

    sql = text("SELECT id, answer FROM textquestions WHERE id=:question_id " +
               "AND visible=True;")
    result = db.session.execute(sql, {"question_id":question_id})
    tq = result.fetchone()

    if tq.answer != tq_answer:
        flash("Väärä vastaus!")
        return redirect("/course/" + str(course_id) + "/text_question/" + str(question_id))

    sql = text("INSERT INTO usersquestions VALUES (DEFAULT, :course_id, :user_id, " +
               "1, :question_id);")
    db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                            "question_id":question_id})
    db.session.commit()
    flash("Oikea vastaus!")
    return redirect("/course/" + str(course_id))

@app.route("/answer_mcq", methods=["POST"])
def answer_mcq():
    mcq_answer = request.form["mcq_answer"]
    user_id = session["id"]
    question_id = request.form["question_id"]
    course_id = request.form["course_id"]
    user = session["user"]

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if user != "student":
        abort(403)

    sql = text("SELECT id FROM usersquestions WHERE course_id=:course_id AND " +
               "user_id=:user_id AND type=2 AND question_id=:question_id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                                      "question_id":question_id})
    answer_already = result.fetchone()

    if answer_already:
        flash("Vastasit jo oikein!")
        print(user, "käyttä on student")
        return redirect("/course/" + str(course_id))

    sql = text("SELECT id, answer FROM multiplechoicequestions WHERE id=:question_id AND " +
               "visible=True;")
    result = db.session.execute(sql, {"question_id":question_id})
    mcq = result.fetchone()

    if mcq.answer != mcq_answer:
        flash("Väärä vastaus!")
        return redirect("/course/" + str(course_id) + "/multiple_choice/" + str(question_id))

    sql = text("INSERT INTO usersquestions VALUES (DEFAULT, :course_id, :user_id, " +
               "2, :question_id);")
    db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                            "question_id":question_id})
    db.session.commit()
    flash("Oikea vastaus!")
    return redirect("/course/" + str(course_id))
