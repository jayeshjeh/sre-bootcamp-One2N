from flask import Blueprint, request, jsonify
from app.models import Student
from app import db
from app.utils import serialize_student, error_response, success_response, update_student_from_data

student_bp = Blueprint("student", __name__)

def get_student_by_id(student_id):
    return Student.query.get(student_id)

@student_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    try:
        student = Student(**data)
        db.session.add(student)
        db.session.commit()
        return success_response(student, 201)
    except Exception as e:
        db.session.rollback()
        return error_response("Student could not be created", 500)

@student_bp.route('/students', methods=['GET'])
def list_students():
    students = Student.query.all()
    return jsonify([serialize_student(s) for s in students])

@student_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response("Student not found", 404)
    return success_response(student)

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response("Student not found", 404)
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": f"Student {student_id} deleted"})
    except Exception as e:
        db.session.rollback()
        return error_response("Deletion failed", 500)

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response("Student not found", 404)
    try:
        data = request.get_json()
        update_student_from_data(student, data)
        db.session.commit()
        return success_response(student)
    except Exception as e:
        db.session.rollback()
        return error_response("Update failed", 500)

