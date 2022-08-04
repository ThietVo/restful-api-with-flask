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

#---------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    class_id= db.Column(db.Integer, db.ForeignKey("class.id"))

    # created_at = db.Column(db.DateTime(timezone=True),
    #                        server_default=func.now())

    def __repr__(self):
        return f'<Student {self.firstname}>'

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(100))
    students = db.relationship('Student', backref='class')

#--------
@app.route('/students/')
def getStudents():
    return jsonify([
        {'id': student.id, 'firstname': student.firstname,
        'lastname': student.lastname, 'email': student.email,
        'age': student.age
        }
        for student in Student.query.all()
    ])

@app.route('/students/<id>')
def getStudent(id):
    student = Student.query.filter_by(id = id).first_or_404()
    return {
        'id': student.id, 'firstname': student.firstname,
        'lastname': student.lastname, 'email': student.email,
        'age': student.age
    }

@app.route('/students/', methods=['POST'])
def createStudent():
    data = request.get_json()
    student = Student(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        age=data['age']
        # created_at=data[func.now()]
    )
    db.session.add(student)
    db.session.commit()

    return ['insert sucssess!']

@app.route('/students/<id>', methods=['PUT'])
def updateStudent(id):
    data = request.get_json()
    student = Student.query.filter_by(id = id).first_or_404()
    student.email = data['email']
    student.class_id = data['class_id']
    db.session.commit()
    
    return jsonify({
        'id': student.id,
        'email': student.email,
        'class_id': student.class_id
    })

@app.route('/students/<id>', methods = ['DELETE'])
def deleteStudent(id):
    student = Student.query.filter_by(id = id).first_or_404()
    db.session.delete(student)
    db.session.commit()

    return {
        'success': 'Data deleted successfully'
    }

#--Class
@app.route('/classes/')
def getClasses():
    return jsonify([
        {
            'id': student.id,
            'classname': student.classname
        }
        for student in Class.query.all()
    ])

@app.route('/classes/<int:id>')
def getClass(id):
    c = Class.query.filter_by(id = id).first_or_404()
    return {
            'id': c.id,
            'classname': c.classname
        }

@app.route('/classes/', methods=['POST'])
def createClass():
    data = request.get_json()
    c = Class(
        classname = data['classname']
    )
    db.session.add(c)
    db.session.commit()

    return ['insert sucssessfully!']


@app.route('/classes/<int:id>', methods=['PUT'])
def updateClass(id):
    data = request.get_json()
    c = Class.query.filter_by(id = id).first_or_404()
    c.classname = data['classname']
    db.session.commit()
    
    return jsonify({
        'id': c.id,
        'classname': c.classname
    })

@app.route('/classes/<int:id>', methods = ['DELETE'])
def deleteClass(id):
    c = Class.query.filter_by(id=id).first_or_404()
    db.session.delete(c)
    db.session.commit
    
    return {
        'success': 'Data deleted successfully'
    }