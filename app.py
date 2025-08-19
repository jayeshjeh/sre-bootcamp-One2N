from dotenv import load_dotenv
from flask import Blueprint, Flask, g, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging, os, time

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10))
    email = db.Column(db.String(150), unique=True)
    
    

def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    if "gunicorn" in os.getenv("SERVER_SOFTWARE", "").lower():
        logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = logger.handlers
        app.logger.setlevel(level)
    else:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s")
        handler.setFormatter(fmt)
        app.logger.handlers = [handler]
        app.logger.setLevel(level)


setup_logging()
log = app.logger

@app.before_request
def start_time():
    g.start_time = time.time()
    

@app.after_request
def log_request(response):
    if hasattr(g, "start_time"):
        duration_ms = round((time.time() - g.start_time) * 1000)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)  # proxy-aware
        log.info(f"{ip} {request.method} {request.path} {response.status_code} {duration_ms}ms")
    return response


#HealthCHeck
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status" : "ok", "database": "ok"}), 200
    except Exception as e:
        log.error(f"Healthcheck failed {e}")
        return jsonify({"status": "error", "database": "unreachable"}), 500
        
        

def get_student_by_id(student_id):
    return Student.query.get(student_id)

def serialize_student(student):
    return {
        "id" : student.id,
        "name" : student.name,
        "age" : student.age,
        "grade" : student.grade,
        "email" : student.email
    }
    
def error_response(message, status=400):
    return jsonify({"error": message}), status

def success_response(student, status=200):
    return jsonify(serialize_student(student)), status

def update_student_from_data(student, data):
    student.name = data.get("name", student.name)
    student.age = data.get("age", student.age)
    student.grade = data.get("grade", student.grade)
    student.email = data.get("email", student.email)
    

v1 = Blueprint("v1", __name__, url_prefix="/api/v1")


@v1.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    try:
        student = Student(**data)
        db.session.add(student)
        db.session.commit()
        log.info(f"Student added - ID: {student.id}")
        return success_response(student, 201)
    except Exception as e:
        db.session.rollback()
        log.error(f"Add student.failed: {e}")
        return error_response("Student could not be created", 500)
    
    
@v1.route('/students', methods=['GET'])
def list_students():
    students = Student.query.all()
    log.info(f"Fetched {len(students)} students")
    return jsonify([serialize_student(s) for s in students])

@v1.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response(f"Student not found", 404)
    return success_response(student)

@v1.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response("Student not found", 404)
    try:
        db.session.delete(student)
        db.session.commit()
        log.info(f"Student deleted - ID: {student_id}")
        return jsonify({"message": f"Student {student_id} deleted"})
    except Exception as e:
        db.session.rollback()
        log.error(f"Delete failed: {e}")
        return error_response("Deletion failed", 500)        

@v1.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return error_response(f"Student not found", 404)
    
    try:
        data =  request.get_json()
        update_student_from_data(student, data)
        db.session.commit()
        log.info(f"Student updated -ID: {student_id}")
        return success_response(student)
    except Exception as e:
        db.session.rollback()
        log.error(f"Update failed: {e}")
        return error_response("Student not found", 404)
    

app.register_blueprint(v1)

if __name__ == '__main__':
    log.info("Starting flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    