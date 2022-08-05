import json
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------

student_course = db.Table(
    "student_course",
    db.Column("student_id", db.Integer, db.ForeignKey(
        "student.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey(
        "course.id"), primary_key=True),
)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    courses = db.relationship(
        "Course",
        secondary=student_course,
        backref="students",
    )

    def __repr__(self):
        return f'<Student {self.firstname}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

# --------


@app.route('/students/')
def getStudents():
    return jsonify([
        {
            'id': student.id,
            'firstname': student.firstname,
            'lastname': student.lastname,
            'email': student.email,
            'age': student.age,
            'created_at': student.created_at,
            'updated_at': student.updated_at
        }
        for student in Student.query.all()
    ])


@app.route('/students/<id>')
def getStudent(id):
    student = Student.query.filter_by(id=id).first_or_404()
    print(student)
    return {
        'id': student.id,
        'firstname': student.firstname,
        'lastname': student.lastname,
        'email': student.email,
        'age': student.age,
        'created_at': student.created_at,
        'updated_at': student.updated_at,
        'courses': student.courses
    }


@app.route('/students/', methods=['POST'])
def createStudent():
    data = request.get_json()
    student = Student(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        age=data['age'],
        created_at=func.now(),
        updated_at=func.now()
    )
    db.session.add(student)
    db.session.commit()

    return ['insert sucssess!']


@app.route('/students/<id>', methods=['PUT'])
def updateStudent(id):
    data = request.get_json()
    student = Student.query.filter_by(id=id).first_or_404()

    if 'firstname' in data:
        student.firstname = data['firstname']
    if 'lastname' in data:
        student.lastname = data['lastname']
    if 'age' in data:
        student.age = data['age']
    if 'email' in data:
        student.email = data['email']

    student.updated_at = func.now()

    db.session.commit()

    return jsonify({
        'id': student.id,
        'firstname': student.firstname,
        'lastname': student.lastname,
        'email': student.email,
        'age': student.age,
        'created_at': student.created_at,
        'updated_at': student.updated_at
    })


@app.route('/students/<id>', methods=['DELETE'])
def deleteStudent(id):
    student = Student.query.filter_by(id=id).first_or_404()
    db.session.delete(student)
    db.session.commit()

    return {
        'success': 'Data deleted successfully'
    }

# --Class


@app.route('/courses/')
def getCourses():
    return jsonify([
        {
            'id': c.id,
            'course_name': c.course_name,
            'created_at': c.created_at,
            'updated_at': c.updated_at
        }
        for c in Course.query.all()
    ])


@app.route('/courses/<int:id>')
def getCourse(id):
    c = Course.query.filter_by(id=id).first_or_404()
    return {
        'id': c.id,
        'course_name': c.course_name,
        'created_at': c.created_at,
        'updated_at': c.updated_at
    }


@app.route('/courses/', methods=['POST'])
def createCourse():
    data = request.get_json()
    c = Course(
        course_name=data['course_name']
    )
    db.session.add(c)
    db.session.commit()

    return {
        "success": 'insert sucssessfully!'
    }


@app.route('/courses/<int:id>', methods=['PUT'])
def updateCourse(id):
    data = request.get_json()
    c = Course.query.filter_by(id=id).first_or_404()

    if 'course_name' in data:
        c.course_name = data['course_name']
    c.updated_at = func.now()

    db.session.commit()

    return jsonify({
        'id': c.id,
        'course_name': c.course_name,
        'created_at': c.created_at,
        'updated_at': c.updated_at
    })


@app.route('/courses/<int:id>', methods=['DELETE'])
def deleteCourse(id):
    c = Course.query.filter_by(id=id).first_or_404()
    db.session.delete(c)
    db.session.commit

    return {
        'success': 'Data deleted successfully'
    }

# register courses


@app.route('/register_course/')
def getRegisterCourses():
    s = db.session.query(Student.id, Student.firstname, Student.lastname, Student.email, Student.age, Course.course_name, student_course).filter(
        student_course.c.student_id == Student.id).filter(student_course.c.course_id == Course.id).all()

    return jsonify([{
        'id': x[0],
        'firstname': x[1],
        'lastname': x[2],
        'email': x[3],
        'age': x[4],
        'course_name': x[5]
    }for x in s
    ])


@app.route('/register_course/<int:id>')
def getRegisterCourse(id):
    s = db.session.query(
            Student.id, Student.firstname, Student.lastname, Student.email, Student.age, Course.course_name, student_course
        ).filter(
            student_course.c.student_id == Student.id
        ).filter(
            student_course.c.course_id == Course.id
        ).filter(
            Student.id == id
        ).all()

    return jsonify([{
        'id': x[0],
        'firstname': x[1],
        'lastname': x[2],
        'email': x[3],
        'age': x[4],
        'course_name': x[5]
    }for x in s
    ])


@app.route('/register_course/', methods=['POST'])
def createRegisterCourse():
    data = request.get_json()
    student = Student.query.filter_by(id=data['student_id']).first_or_404()
    course = Course.query.filter_by(id=data['course_id']).first_or_404()

    student.courses.append(course)
    db.session.commit()

    return {
        "success": 'insert sucssessfully!'
    }

@app.route('/register_course/', methods=['DELETE'])
def deleteCourseRegisted():
    data = request.get_json()
    student = db.session.query(Student).filter(Student.id == data["student_id"]).one()
    course = db.session.query(Course).filter(Course.id == data["course_id"]).one()
    student.courses.remove(course)
    db.session.commit()

    return {
        'success': 'Data deleted successfully'
    }
