from db import db
from flask import flash
from sqlalchemy.sql import text
import users

def get_text_questions(course_id):
    sql = text("SELECT id, question FROM textquestions WHERE course_id=:course_id AND " +
               "visible=True ORDER BY id;")
    result = db.session.execute(sql, {"course_id":course_id})
    text_questions = result.fetchall()
    return text_questions

def get_mc_questions(course_id):
    sql = text("SELECT id, question FROM multiplechoicequestions WHERE course_id=:course_id AND " +
               "visible=True ORDER BY id;")
    result = db.session.execute(sql, {"course_id":course_id})
    mc_questions = result.fetchall()
    return mc_questions

def get_tq_answers(course_id, username_id):
    sql = text("SELECT t.question FROM textquestions t, usersquestions u WHERE t.id=u.question_id" +
               " AND u.course_id=:course_id AND u.user_id=:user_id AND u.type=1 AND " +
               "t.visible=True ORDER BY t.id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":username_id})
    tq_answers = result.fetchall()
    return tq_answers

def get_mcq_answers(course_id, username_id):
    sql = text("SELECT m.question FROM multiplechoicequestions m, usersquestions u " +
               "WHERE m.id=u.question_id AND u.course_id=:course_id AND u.user_id=:user_id AND " +
               "u.type=2 AND m.visible=True")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":username_id})
    mcq_answers = result.fetchall()
    return mcq_answers

def remove_tq(tq_id, course_id):
    sql = text("UPDATE textquestions SET visible=False WHERE id=:tq_id " +
               "AND course_id=:course_id;")
    db.session.execute(sql, {"tq_id": tq_id, "course_id":course_id})
    db.session.commit()

def add_tq(course_id, question, answer):
    sql = text("INSERT INTO textquestions VALUES (DEFAULT, :course_id, :question, " +
               ":answer, true);")
    db.session.execute(sql, {"course_id":course_id, "question":question, "answer":answer})
    db.session.commit()

def add_mcq(course_id, choices, question, answer):
    sql = text("INSERT INTO multiplechoicequestions VALUES (DEFAULT, " +
               ":course_id, :answer, :question, true) RETURNING id;")
    result = db.session.execute(sql, {"course_id":course_id, "answer":choices[int(answer)-1],
                                      "question":question})
    db.session.commit()
    last_inserted_id = result.fetchone()[0]

    for choice in choices:
        if choice != "":
            sql = text("INSERT INTO multiplechoiceoptions VALUES (DEFAULT, :id, :choice)")
            db.session.execute(sql, {"id":last_inserted_id, "choice":choice})
    db.session.commit()

def remove_mcq(mcq_id, course_id):
    sql = text("UPDATE multiplechoicequestions SET visible=False WHERE id=:mcq_id " +
               "AND course_id=:course_id;")
    db.session.execute(sql, {"mcq_id": mcq_id, "course_id":course_id})
    db.session.commit()

def get_text_question(username_id, text_question_id):
    admin = users.get_user(username_id)
    sql = text("SELECT id, course_id, answer, question FROM textquestions WHERE" +
               " id=:text_question_id AND visible=True;")
    result = db.session.execute(sql, {"text_question_id":text_question_id})
    question = result.fetchone()
    return question, admin

def change_tq_title(question_id, course_id, tq_title):
    sql = text("UPDATE textquestions SET question=:tq_title WHERE id=:question_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "tq_title":tq_title})
    db.session.commit()

def change_tq_answer(question_id, course_id, tq_answer):
    sql = text("UPDATE textquestions SET answer=:tq_answer WHERE id=:question_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "tq_answer":tq_answer})
    db.session.commit()

def get_multiple_choice(username_id, mcq_id):
    admin = users.get_user(username_id)
    sql = text("SELECT id, option FROM multiplechoiceoptions WHERE " +
               "multiplechoicequestion_id=:mcq_id;")
    result = db.session.execute(sql, {"mcq_id":mcq_id})
    choices = result.fetchall()
    sql = text("SELECT id, question, answer FROM multiplechoicequestions WHERE " +
               "id=:mcq_id AND visible=True;")
    result = db.session.execute(sql, {"mcq_id":mcq_id})
    question = result.fetchone()
    return admin, choices, question

def change_mcq_title(question_id, course_id, mcq_title):
    sql = text("UPDATE multiplechoicequestions SET question=:mcq_title " +
               "WHERE id=:question_id AND course_id=:course_id;")
    db.session.execute(sql, {"question_id": question_id, "course_id":course_id,
                             "mcq_title":mcq_title})
    db.session.commit()

def change_mcq_answer(course_id, choices, answer, question_id):
    sql = text("UPDATE multiplechoicequestions SET answer=:answer " +
               "WHERE id=:question_id AND course_id=:course_id;")
    db.session.execute(sql, {"course_id":course_id, "answer":choices[int(answer)-1],
                                      "question_id":question_id})
    db.session.commit()
    sql = text("SELECT id, option FROM multiplechoiceoptions WHERE "
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

def answer_tq(course_id, user_id, question_id, tq_answer):
    sql = text("SELECT id FROM usersquestions WHERE course_id=:course_id AND " +
               "user_id=:user_id AND type=1 AND question_id=:question_id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                                      "question_id":question_id})
    answer_already = result.fetchone()

    if answer_already:
        flash("Vastasit jo oikein!")
        return True

    sql = text("SELECT id, answer FROM textquestions WHERE id=:question_id " +
               "AND visible=True;")
    result = db.session.execute(sql, {"question_id":question_id})
    tq = result.fetchone()

    if tq.answer != tq_answer:
        flash("Väärä vastaus!")
        return False

    sql = text("INSERT INTO usersquestions VALUES (DEFAULT, :course_id, :user_id, " +
               "1, :question_id);")
    db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                            "question_id":question_id})
    db.session.commit()
    flash("Oikea vastaus!")
    return True

def answer_mcq(course_id, user_id, question_id, mcq_answer):
    sql = text("SELECT id FROM usersquestions WHERE course_id=:course_id AND " +
               "user_id=:user_id AND type=2 AND question_id=:question_id;")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                                      "question_id":question_id})
    answer_already = result.fetchone()

    if answer_already:
        flash("Vastasit jo oikein!")
        return True

    sql = text("SELECT id, answer FROM multiplechoicequestions WHERE id=:question_id AND " +
               "visible=True;")
    result = db.session.execute(sql, {"question_id":question_id})
    mcq = result.fetchone()

    if mcq.answer != mcq_answer:
        flash("Väärä vastaus!")
        return False

    sql = text("INSERT INTO usersquestions VALUES (DEFAULT, :course_id, :user_id, " +
               "2, :question_id);")
    db.session.execute(sql, {"course_id":course_id, "user_id":user_id,
                            "question_id":question_id})
    db.session.commit()
    flash("Oikea vastaus!")
    return True
