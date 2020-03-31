import datetime
from app import db

candidature_skill_table = db.Table('candidature_skill',
    db.Column('student_id', db.Integer, db.ForeignKey('student_table.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill_table.id'), primary_key=True)
)

candidature_table = db.Table('candidature',
    db.Column('student_id', db.Integer, db.ForeignKey('student_table.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course_table.id'), primary_key=True)
)

class Student(db.Model):
    __tablename__='student_table'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    fullname = db.Column(db.String(80), nullable=False)

    #many-to-many for courses
    courses = db.relationship('Course', secondary=candidature_table, back_populates='student_course', cascade='all', lazy=True)

    #many-to-many for skills
    skills = db.relationship('Skill', secondary=candidature_skill_table, back_populates='student_skill', cascade='all', lazy=True)

    #one-to-many for rating
    rating = db.relationship('Rating', back_populates='student_rating', uselist=True, cascade='all', lazy=True)

    def __init__(self,email,fullname):
        self.email = email
        self.fullname = fullname
        self.courses = []
        self.skills = [] 
        self.rating =[] 
    
    def __repr__(self):
        return '<{} {} {} {} {}>'.format(self.id, self.email, self.fullname, self.courses,self.skills)


class Course(db.Model):
    __tablename__='course_table'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(10), unique=True, nullable=False)
    course_name = db.Column(db.String(80), unique=True, nullable=False)

    student_course = db.relationship('Student', secondary=candidature_table, back_populates='courses')

    def __init__(self,course_code,course_name):
        self.course_code = course_code
        self.course_name = course_name
        self.student_course = []

    def __repr__(self):
        return '<{} {} {} {}>'.format(self.id, self.course_code, self.course_name, self.student_course)


class Skill(db.Model):
    __tablename__='skill_table'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(80), unique=True, nullable=False)
    skill_type = db.Column(db.String(30), nullable=False)

    student_skill = db.relationship('Student', secondary=candidature_skill_table, back_populates='skills')

    def __init__(self,skill_name,skill_type):
        self.skill_name = skill_name
        self.skill_type = skill_type
        self.student_skill = []

    def __repr__(self):
        return '<{} {} {} {}>'.format(self.id, self.skill_name, self.skill_type, self.student_skill)


class Rating(db.Model):
    __tablename__='rate_table'

    id = db.Column(db.Integer)
    ratee_id = db.Column(db.Integer, db.ForeignKey('student_table.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill_table.id'), primary_key=True)
    rater_id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student_rating = db.relationship('Student', back_populates='rating')

    def __init__(self,ratee_id,skill_id,rater_id,course_code):
        self.ratee_id = ratee_id
        self.skill_id = skill_id
        self.rater_id = rater_id
        self.course_code = course_code
    
    def __repr__(self):
        return '<{} {} {} {} {}>'.format(self.id, self.ratee_id, self.skill_id, self.rater_id,self.course_code)
