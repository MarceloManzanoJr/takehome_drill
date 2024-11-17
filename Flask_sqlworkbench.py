from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from datetime import datetime

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:meraw123456@localhost/student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_number = db.Column(db.String(64), nullable=False, unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    middle_name = db.Column(db.String(64))
    sex = db.Column(db.String(10), nullable=False) 
    birthday = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_number": self.student_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "sex": self.sex,
            "birthday": self.birthday.strftime("%Y-%m-%d"),
        }

@app.route("/api/students", methods=["GET"])
def get_students():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    students = Student.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "data": [student.to_dict() for student in students.items],
        "total": students.total,
        "page": students.page,
        "pages": students.pages
    }), HTTPStatus.OK

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify(
            {
                "success": False, 
                "error": "Student not found"
            }
        ), HTTPStatus.NOT_FOUND
    
    return jsonify(
        {
            "success": True, 
            "data": student.to_dict()
        }
    ), HTTPStatus.OK

@app.route("/api/students", methods=["POST"])
def create_student():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "success": False,
            "error": "Invalid JSON format."
        }), HTTPStatus.BAD_REQUEST
    
    required_fields = ["student_number", "first_name", "last_name", "sex", "birthday"]
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "success": False,
                    "error": f"Missing required field: {field}",
                }
            ), HTTPStatus.BAD_REQUEST

    if data['sex'] not in ['Male', 'Female']:
        return jsonify({
            "success": False,
            "error": "Invalid value for 'sex'. Allowed values are 'Male' or 'Female'."
        }), HTTPStatus.BAD_REQUEST

    try:
        birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid date format for 'birthday'. Expected 'YYYY-MM-DD'."
        }), HTTPStatus.BAD_REQUEST

    new_student = Student(
        student_number=data['student_number'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        middle_name=data.get('middle_name', None), 
        sex=data['sex'], 
        birthday=birthday
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": new_student.to_dict(),
        }
    ), HTTPStatus.CREATED

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = Student.query.get(student_id)

    if student is None: 
        return jsonify(
            {
                "success": False,
                "error":"Student not found"
            }
        ), HTTPStatus.NOT_FOUND
    
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "success": False,
            "error": "Invalid JSON format."
        }), HTTPStatus.BAD_REQUEST

    update_fields = ["student_number", "first_name", "last_name", "middle_name", "sex", "birthday"]
    for key in update_fields:
        if key in data:
            if key == 'birthday':
                try:
                    setattr(student, key, datetime.strptime(data[key], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({
                        "success": False,
                        "error": "Invalid date format for 'birthday'. Expected 'YYYY-MM-DD'."
                    }), HTTPStatus.BAD_REQUEST
            else:
                setattr(student, key, data[key])
    
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": student.to_dict()
        }
    ), HTTPStatus.OK

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)

    if student is None: 
        return jsonify(
            {
                "success": False, 
                "error": "Student not found."
            }
        ), HTTPStatus.NOT_FOUND
    
    db.session.delete(student)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": "Student deleted successfully."
        }
    ), HTTPStatus.OK

@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": "Resource not found"
        }
    ), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(
        {
            "success": False,
            "error": "Internal Server Error"
        }
    ), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
