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

    #many-to-many for skills
    skills = db.relationship('Skill', secondary=candidature_skill_table, back_populates='student_skill', cascade='all', lazy=True)

    #many-to-many for courses
    courses = db.relationship('Course', secondary=candidature_table, back_populates='student_course', cascade='all', lazy=True)

    #one-to-many for rating
    rating = db.relationship('Rating', back_populates='student_rating', uselist=True, lazy=True)

    def __init__(self,email,fullname):
        self.email = email
        self.fullname = fullname
        self.courses = []
        self.skills = [] 
        self.rating =[] 
    
    def __repr__(self):
        return '<{} {} {} {} {}>'.format(self.id, self.email, self.fullname, self.courses,self.skills)
    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "fullname": self.fullname,
            "courses": [i.course_code for i in self.courses],
            "skills": [i.skill_name for i in self.skills],
            "rating": [i.serialize() for i in self.rating]
        }


class Course(db.Model):
    __tablename__='course_table'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(80), unique=True, nullable=False)

    student_course = db.relationship('Student', secondary=candidature_table, back_populates='courses')

    def __init__(self,course_code,course_name):
        self.course_code = course_code
        self.course_name = course_name
        self.student_course = []

    def __repr__(self):
        return '<{} {} {} {}>'.format(self.id, self.course_code, self.course_name, self.student_course)
    
    def serialize(self):
        return {
            'id' : self.id,
            'course_code': self.course_code,
            'course_name': self.course_name
        }


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
    
    def serialize(self):

        return {
            "skill_name": self.skill_name,
            "skill_type": self.skill_type
        }

class Rating(db.Model):
    __tablename__='rate_table'

    id = db.Column(db.Integer,primary_key=True)
    ratee_id = db.Column(db.Integer, db.ForeignKey('student_table.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    rate_details = db.relationship('Rate_Detail',back_populates='rates', uselist=True, cascade='all', lazy=True)
    student_rating = db.relationship('Student', back_populates='rating')

    def __init__(self,ratee_id):
        self.ratee_id = ratee_id
        self.rate_details = []

    def serialize(self):
        return{
            'id': self.id,
            'timestamp': self.timestamp,
            'rate_details':[i.serialize() for i in self.rate_details]
        }

class Rate_Detail(db.Model):
    __tablename__='rate_det'

    ratee_id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(30), nullable=False)
    rate_id = db.Column(db.Integer, db.ForeignKey('rate_table.id'))

    rates = db.relationship('Rating', back_populates='rate_details')

    def __init__(self,ratee_id,skill_id,rater_id,course_code,rate_id):
        self.ratee_id = ratee_id
        self.skill_id = skill_id
        self.rater_id = rater_id
        self.course_code = course_code
        self.rate_id = rate_id

    def __repr__(self):
        return '<{} {} {} {} {}>'.format(self.id, self.ratee_id, self.skill_id, self.rater_id,self.course_code,self.rate_id)
    
    def serialize(self):
        skill = Skill.query.filter_by(id=self.skill_id).first()
        rater = Student.query.filter_by(id=self.rater_id).first()

        return {
            'skill': skill.skill_name,
            'rater': rater.email,
            'course_code': self.course_code,
        }

class States(db.Model):
    __tablename__='state'

    id = db.Column(db.Integer, primary_key=True)
    chatid = db.Column(db.Integer)
    stage = db.Column(db.String(50), nullable=False)
    ratee_email1 = db.Column(db.String(80),nullable=True)
    course_code1= db.Column(db.String(50),nullable=True)
    rate_skill1 = db.Column(db.String(100),nullable=True)
    rater_email1 = db.Column(db.String(80),nullable=True)

    def __init__(self,chatid,stage,ratee_email1,course_code1,rate_skill1,rater_email1):
        self.chatid = chatid
        self.stage = stage
        self.ratee_email1 = ratee_email1
        self.course_code1 = course_code1
        self.rate_skill1 = rate_skill1
        self.rater_email1 = rater_email1

    
    def serialize(self):
        return {
            'chat_id':self.chatid,
            'stage':self.stage,
            'ratee_email': self.ratee_email1,
            'course_code': self.course_code1,
            'rate_skill1': self.rate_skill1,
            'rater_email1': self.rater_email1
        }

