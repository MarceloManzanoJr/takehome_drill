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
