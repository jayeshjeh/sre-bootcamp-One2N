from flask import Blueprint, Flask, request, jsonify
import logging, os, time


app = Flask(__name__)

students = {}

v1 = Blueprint("v1", __name__, url_prefix="/api/v1")


def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    if "gunicorn" in os.getenv("SERVER_SOFTWARE", "").lower():
        logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = logger.handlers
        app.logger.setlevel(level)
    else:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(fmt)
        app.logger.handlers = [handler]
        app.logger.setLevel(level)


setup_logging()
log = app.logger

@v1.route('/students', methods=['POST'])
def add_students():
    data = request.get_json()
    student_id = str(len(students) + 1)
    students[student_id] = data
    return jsonify({"id": student_id, "student":data}), 201 

@v1.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

@v1.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({student_id: student})

@v1.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    if student_id not in students:
        return jsonify({"error": "Student not found"}), 404
    data = request.get_json()
    students[student_id] = data
    return jsonify({student_id: data})

@v1.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    if student_id not in students:
        return jsonify({"error": "Student not found"}), 404
    del students[student_id]
    return jsonify({"message": f"Student {student_id} deleted."})

app.register_blueprint(v1)

if __name__ == '__main__':
    app.run(debug=True)
