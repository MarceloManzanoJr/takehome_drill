import pytest
import json
from Flask_excercise import app, db, Student

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/records'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_get_all_students(test_client):
    response = test_client.get('/api/students')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert isinstance(data['data'], list)

def test_create_student(test_client):
    new_student = {
        "student_name": "2022-8-0097",
        "first_name": "Marcelo",
        "last_name": "Manzano",
        "middle_name": "R",
        "sex": "Male",
        "birthday": "2004-03-12"
    }
    response = test_client.post('/api/students', json=new_student)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['successs'] is True
    assert data['data']['student_number'] == "2022-8-0097"

def test_get_single_student(test_client):
    student = Student(
        student_number="2022-8-2114",
        first_name="Jamaica",
        last_name="Magbanua",
        middle_name="C",
        sex="Famale",
        birthday="2004-08-23"
    )
    db.session.add(student)
    db.session.commit()

    response = test_client.get(f'/api/students/{student.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['first_name'] == "Jamaica"

def test_update_student(test_client):
    with app.app_context():
        student = Student(
            student_number="2023-9-0001",
            first_name="Original Name",
            last_name="Doe",
            middle_name="A",
            sex="Male",
            birthday="2000-01-01"
        )
        db.session.add(student)
        db.session.commit()

        student_id = student.id

    update_data = {
        "first_name": "Updated Name"
    }


    response = test_client.put(f'/api/students/{student_id}', json=update_data)

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['first_name'] == "Updated Name"


    with app.app_context():
        updated_student = Student.query.get(student_id)
        assert updated_student.first_name == "Updated Name"

def test_delete_student(test_client):
    student = Student.query.first()
    response = test_client.delete(f'/api/students/{student.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data'] == "Student deleted successfully."

    response = test_client.get(f'/api/students/{student.id}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False