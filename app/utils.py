def serialize_student(student):
    return {
        "id": student.id,
        "name": student.name,
        "age": student.age,
        "grade": student.grade,
        "email": student.email
    }

def error_response(message, status=400):
    return {"error": message}, status

def success_response(student, status=200):
    return serialize_student(student), status

def update_student_from_data(student, data):
    student.name = data.get("name", student.name)
    student.age = data.get("age", student.age)
    student.grade = data.get("grade", student.grade)
    student.email = data.get("email", student.email)
