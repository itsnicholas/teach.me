from app import app
from flask import redirect, render_template, request, abort
import users, courses, materials, questions

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    message = None
    if len(username) > 16:
        message = "Tunnus on liian pitkä"
    elif len(username) < 1:
        message = "Tunnus on liian lyhyt"
    elif len(password) > 16:
        message = "Salasana on liian pitkä"
    elif len(password) < 8:
        message = "Salasana on liian lyhyt"

    if message:
        return render_template("index.html", message=message)

    if users.login(username, password):
        return redirect("/courses")

    return render_template("index.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        message = None
        if len(username) > 16:
            message = "Tunnus on liian pitkä"
        elif len(username) < 1:
            message = "Tunnus on liian lyhyt"
        elif len(password) > 16:
            message = "Salasana on liian pitkä"
        elif len(password) < 8:
            message = "Salasana on liian lyhyt"

        if message:
            return render_template("signup.html", message=message)

        if users.signup(username, password):
            return redirect("/")
        else:
            return render_template("signup.html", message="Käyttäjätunnus on käytössä" +
                                    " - kokeile toista käyttäjätunnusta")

@app.route("/courses")
def course_list():
    courses_info, admin = courses.course_list(users.user_id())
    return render_template("courses.html", courses_info=courses_info, admin=admin)

@app.route("/add_course", methods=["POST"])
def add_course():
    course_name = request.form["course_name"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(course_name) > 50:
        message = "Kurssin nimi on liian pitkä"
    elif len(course_name) < 1:
        message = "Kurssin nimi on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    courses.add_course(course_name)
    return redirect("/courses")

@app.route("/remove_course", methods=["POST"])
def remove_course():
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    courses.remove_course(course_id)
    return redirect("/courses")

@app.route("/course/<int:course_id>")
def course(course_id):

    course_data = courses.course(users.user_id(), course_id)

    return render_template("course.html",
                           course_info=course_data['course_info'], join=course_data['join'],
                           materials=course_data['materials'],
                           text_questions=course_data['text_questions'], tq_total=
                           len(course_data['text_questions']),
                           tq_answers=course_data['tq_answers'],
                           tq_answers_total=len(course_data['tq_answers']),
                           mc_questions=course_data['mc_questions'],
                           mcq_total=len(course_data['mc_questions']),
                           mcq_answers=course_data['mcq_answers'],
                           mcq_answers_total=len(course_data['mcq_answers']),
                           course_enrolled=course_data['course_enrolled'], 
                           admin=course_data['admin'])

@app.route("/change_ct", methods=["POST"])
def change_ct():
    course_title = request.form["course_title"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(course_title) > 50:
        message="Kurssin nimi on liian pitkä"
    elif len(course_title) < 1:
        message="Kurssin nimi on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    courses.change_ct(course_title, course_id)

    return redirect("/course/" + str(course_id))

@app.route("/enrol", methods=["POST"])
def enrol():
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "student":
        abort(403)

    courses.enrol(users.user_id(), course_id)

    return redirect("/course/" + str(course_id))

@app.route("/remove_material", methods=["POST"])
def remove_material():
    course_id = request.form["course_id"]
    material_id = request.form["material_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    materials.remove_material(material_id, course_id)

    return redirect("/course/" + str(course_id))

@app.route("/add_material", methods=["POST"])
def add_material():
    material_answer = request.form["material_answer"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(material_answer) > 500:
        message="Materiaali on liian pitkä"
    elif len(material_answer) < 1:
        message="Materiaali on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    materials.add_material(course_id, material_answer)

    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/material/<int:material_id>")
def material_page(course_id, material_id):

    admin, material_text = materials.material_page(course_id, material_id, users.user_id())

    return render_template("material.html", material_id=material_id, course_id=course_id,
                           material_text=material_text, admin=admin)

@app.route("/change_material", methods=["POST"])
def change_material():
    course_id = request.form["course_id"]
    material_id = request.form["material_id"]
    material_text = request.form["material_text"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(material_text) > 500:
        message="Materiaali on liian pitkä"
    elif len(material_text) < 1:
        message="Materiaali on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    materials.change_material(material_id, course_id, material_text)

    return redirect("/course/" + str(course_id))

@app.route("/remove_tq", methods=["POST"])
def remove_tq():
    course_id = request.form["course_id"]
    tq_id = request.form["tq_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    questions.remove_tq(tq_id, course_id)

    return redirect("/course/" + str(course_id))

@app.route("/add_tq", methods=["POST"])
def add_tq():
    question = request.form["question"]
    answer = request.form["answer"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(question) > 100:
        message="Kysymys on liian pitkä"
    elif len(question) < 1:
        message="Kysymys on liian lyhyt"
    elif len(answer) > 200:
        message="Vastaus on liian pitkä"
    elif len(answer) < 1:
        message="Vastaus on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    questions.add_tq(course_id, question, answer)

    return redirect("/course/" + str(course_id))

@app.route("/add_mcq", methods=["POST"])
def add_mcq():
    question = request.form["question"]
    choices = request.form.getlist("choice")
    answer = request.form["answer"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(question) > 100:
        message="Kysymys on liian pitkä"
    elif len(question) < 1:
        message="Kysymys on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    for choice in choices:
        if len(choice) > 50:
            message="Vastaus on liian pitkä"
        elif len(choice) < 1:
            message="Vastaus on liian lyhyt"

        if message:
            return render_template("error.html", message=message)

    questions.add_mcq(course_id, choices, question, answer)

    return redirect("/course/" + str(course_id))

@app.route("/remove_mcq", methods=["POST"])
def remove_mcq():
    course_id = request.form["course_id"]
    mcq_id = request.form["mcq_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    questions.remove_mcq(mcq_id, course_id)

    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/enrolled/<int:student_id>")
def enrolled(course_id, student_id):

    enrolled_data = courses.enrolled(course_id, student_id)

    return render_template("enrolled.html", course_info=enrolled_data['course_info'],
                           text_questions=enrolled_data['text_questions'], 
                           student=enrolled_data['student'],
                           tq_total=len(enrolled_data['text_questions']),
                           tq_answers=enrolled_data['tq_answers'],
                           tq_answers_total=len(enrolled_data['tq_answers']),
                           mc_questions=enrolled_data['mc_questions'],
                           mcq_total=len(enrolled_data['mc_questions']),
                           mcq_answers=enrolled_data['mcq_answers'],
                           mcq_answers_total=len(enrolled_data['mcq_answers']))

@app.route("/course/<int:course_id>/text_question/<int:text_question_id>")
def multiple_choice(course_id, text_question_id):

    question, admin = questions.multiple_choice(users.user_id(), text_question_id)

    return render_template("text_question.html",
                           course_id=course_id, question=question, admin=admin)

@app.route("/change_tq_title", methods=["POST"])
def change_tq_title():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    tq_title = request.form["tq_title"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(tq_title) > 100:
        message = "Kysymys on liian pitkä"
    elif len(tq_title) < 1:
        message = "Kysymys on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    questions.change_tq_title(question_id, course_id, tq_title)

    return redirect("/course/" + str(course_id))

@app.route("/change_tq_answer", methods=["POST"])
def change_tq_answer():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    tq_answer = request.form["tq_answer"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(tq_answer) > 200:
        message="Vastaus on liian pitkä"
    elif len(tq_answer) < 1:
        message="Vastaus on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    questions.change_tq_answer(question_id, course_id, tq_answer)

    return redirect("/course/" + str(course_id))

@app.route("/course/<int:course_id>/multiple_choice/<int:mcq_id>")
def text_question(course_id, mcq_id):

    admin, choices, question = questions.text_question(users.user_id(), mcq_id)

    return render_template("multiple_choice.html",
                           course_id=course_id, choices=choices,
                           question=question, admin=admin)

@app.route("/change_mcq_title", methods=["POST"])
def change_mcq_title():
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]
    mcq_title = request.form["mcq_title"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    if len(mcq_title) > 100:
        message="Kysymys on liian pitkä"
    elif len(mcq_title) < 1:
        message="Kysymys on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    questions.change_mcq_title(question_id, course_id, mcq_title)

    return redirect("/course/" + str(course_id))

@app.route("/change_mcq_answer", methods=["POST"])
def change_mcq_answer():
    choices = request.form.getlist("choice")
    answer = request.form["answer"]
    course_id = request.form["course_id"]
    question_id = request.form["question_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "admin":
        abort(403)

    message = None
    for choice in choices:
        if len(choice) > 50:
            message="Vastaus on liian pitkä"
        elif len(choice) < 1:
            message="Vastaus on liian lyhyt"

        if message:
            return render_template("error.html", message=message)

    questions.change_mcq_answer(course_id, choices, answer, question_id)

    return redirect("/course/" + str(course_id))

@app.route("/answer_tq", methods=["POST"])
def answer_tq():
    tq_answer = request.form["tq_answer"]
    user_id = users.user_id()
    question_id = request.form["question_id"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "student":
        abort(403)

    message = None
    if len(tq_answer) > 200:
        message="Vastaus on liian pitkä"
    elif len(tq_answer) < 1:
        message="Vastaus on liian lyhyt"

    if message:
        return render_template("error.html", message=message)

    answer = questions.answer_tq(course_id, user_id, question_id, tq_answer)

    if answer:
        return redirect("/course/" + str(course_id))

    return redirect("/course/" + str(course_id) + "/text_question/" + str(question_id))

@app.route("/answer_mcq", methods=["POST"])
def answer_mcq():
    mcq_answer = request.form["mcq_answer"]
    user_id = users.user_id()
    question_id = request.form["question_id"]
    course_id = request.form["course_id"]

    if users.session_token() != request.form["csrf_token"]:
        abort(403)

    if users.get_user_session() != "student":
        abort(403)

    answer = questions.answer_mcq(course_id, user_id, question_id, mcq_answer)

    if answer:
        return redirect("/course/" + str(course_id))

    return redirect("/course/" + str(course_id) + "/multiple_choice/" + str(question_id))
