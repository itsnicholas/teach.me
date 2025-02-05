from db import db
from sqlalchemy.sql import text
import users

def get_materials(course_id):
    sql = text("SELECT id, material FROM materials WHERE course_id=:course_id AND visible=True " +
               "ORDER BY id ASC;")
    result = db.session.execute(sql, {"course_id":course_id})
    materials = result.fetchall()
    return materials

def remove_material(material_id, course_id):
    sql = text("UPDATE materials SET visible=False WHERE id=:material_id AND course_id=:course_id;")
    db.session.execute(sql, {"material_id": material_id, "course_id":course_id})
    db.session.commit()

def add_material(course_id, material_answer):
    sql = text("INSERT INTO materials VALUES (DEFAULT, :course_id, :material_answer, true);")
    db.session.execute(sql, {"course_id":course_id, "material_answer":material_answer})
    db.session.commit()

def get_material_page(course_id, material_id, username_id):
    admin = users.get_user(username_id)
    sql = text("SELECT id, material FROM materials WHERE id=:material_id AND course_id=:course_id;")
    result = db.session.execute(sql, {"material_id":material_id, "course_id":course_id})
    material_text = result.fetchone()[1]
    return admin, material_text

def change_material(material_id, course_id, material_text):
    sql = text("UPDATE materials SET material=:material_text WHERE id=:material_id" +
               " AND course_id=:course_id;")
    db.session.execute(sql, {"material_id": material_id, "course_id":course_id,
                             "material_text":material_text})
    db.session.commit()
