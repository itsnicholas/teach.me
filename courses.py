from db import db
from sqlalchemy.sql import text
import users, materials, questions

def get_courses_info(course_id):
    sql = text("SELECT id, name FROM courses WHERE id=:course_id;")
    result = db.session.execute(sql, {"course_id":course_id})
    course_info = result.fetchone()
    return course_info

def course_list(username_id):
    sql = text("SELECT id, name FROM courses WHERE visible=True ORDER BY id;")
    result = db.session.execute(sql)
    courses_info = result.fetchall()
    admin = users.get_user(username_id)
    return courses_info, admin

def add_course(course_name):
    sql = text("SELECT id FROM courses WHERE name=:course_name AND visible=True;")
    result = db.session.execute(sql, {"course_name":course_name})
    course_result = result.fetchone()

    if not course_result:
        sql = text("INSERT INTO courses VALUES (DEFAULT, :course_name, true);")
        db.session.execute(sql, {"course_name":course_name})
        db.session.commit()

def remove_course(course_id):
    sql = text("UPDATE courses SET visible=False WHERE id=:course_id AND visible=True;")
    db.session.execute(sql, {"course_id":course_id})
    db.session.commit()

def course(username_id, course_id):
    admin = users.get_user(username_id)
    course_info = get_courses_info(course_id)
    sql = text("SELECT id FROM userscourses WHERE user_id=:username_id AND course_id=:course_id;")
    result = db.session.execute(sql, {"username_id":username_id, "course_id":course_id})
    join = result.fetchone()
    all_materials = materials.get_materials(course_id)
    text_questions = questions.get_text_questions(course_id)
    tq_answers = questions.get_tq_answers(course_id, username_id)
    mc_questions = questions.get_mc_questions(course_id)
    mcq_answers = questions.get_mcq_answers(course_id, username_id)
    sql = text("SELECT u.id, u.username FROM users u, userscourses o, courses c " +
               "WHERE u.id=o.user_id AND o.course_id=c.id AND c.name=:course_name;")
    result = db.session.execute(sql, {"course_name":course_info.name})
    course_enrolled = result.fetchall()
    course_data = {
        'admin': admin,
        'course_info': course_info,
        'join': join,
        'materials': all_materials,
        'text_questions': text_questions,
        'tq_answers': tq_answers,
        'mc_questions': mc_questions,
        'mcq_answers': mcq_answers,
        'course_enrolled': course_enrolled
    }
    return course_data

def change_ct(course_title, course_id):
    sql = text("UPDATE courses SET name=:course_title WHERE id=:course_id;")
    db.session.execute(sql, {"course_title":course_title, "course_id":course_id})
    db.session.commit()

def enrol(user_id, course_id):
    sql = text("INSERT INTO userscourses VALUES (DEFAULT, :user_id, :course_id);")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()

def enrolled(course_id, username_id):
    course_info = get_courses_info(course_id)
    student = users.get_user(username_id)
    text_questions = questions.get_text_questions(course_id)
    mc_questions = questions.get_mc_questions(course_id)
    tq_answers = questions.get_tq_answers(course_id, username_id)
    mcq_answers = questions.get_mcq_answers(course_id, username_id)
    enrolled_data = {
        'course_info': course_info,
        'student': student,
        'text_questions': text_questions,
        'tq_answers': tq_answers,
        'mc_questions': mc_questions,
        'mcq_answers': mcq_answers
    }
    return enrolled_data
