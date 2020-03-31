# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ratemeuser:ratemepassword@localhost:5432/ratemedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Student, Course, Skill, Rating

# Step 05: add routes and their binded functions here

#Filling up the student table - must fill up email, fullname, and list of courses.
@app.route('/PostStudentDetail/', methods=['POST']) 
def create_student():
	#need to check if the request.json has email, fullname and courses
	#and make sure they have the correct data types
	try:
		if 'email' not in request.json or 'fullname' not in request.json or 'courses' not in request.json:
			return("email,fullname and courses must be included in the request")
		elif type(request.json['email']) != str or type(request.json['fullname']) != str or type(request.json['courses']) != list:
			return("email and fullname to be in string format, courses in list format")
		else:
			email = request.json["email"]
			fullname = request.json["fullname"]
			courses = request.json["courses"]

		valid_email = Student.query.filter_by(email=email).first()

		if valid_email is not None:
			return("User already exists in database")
		else:
			new_entry = Student(email=email,fullname=fullname)
			db.session.add(new_entry)
			db.session.commit()
		
		#check if each of the courses they took is valid
		for i in courses:
			valid_course = Course.query.filter_by(course_code=i).first()
			if valid_course is None:
				return "Please only input valid course codes"
			new_entry.courses.append(valid_course)
			db.session.commit()
		
		return jsonify("{} has been added to the database".format(new_entry.email))

	except Exception as e:
		return(str(e))

#Filling up the course table
#add new courses/names when they do not already exist in the table
@app.route('/PostCourseDetail/', methods=['POST']) 
def create_course():

	try:
		if 'course_code' not in request.json or 'course_name' not in request.json:
			return ("course_code and course_name must be included in the request")
		elif type(request.json["course_code"]) != str or type(request.json["course_name"]) != str:
			return ("course_code and course_name need to be in string format")
		else:
			course_code = request.json["course_code"]
			course_name = request.json["course_name"]

		valid_course_code = Course.query.filter_by(course_code=course_code).first()
		valid_course_name = Course.query.filter_by(course_name=course_code).first()

		if valid_course_code is not None or valid_course_name is not None:
			return("The course code or course name you are trying to add already exists")
		else:
			new_entry = Course(course_code=course_code,course_name=course_name)
			db.session.add(new_entry)
			db.session.commit()
		
		return jsonify("{} has been added to the database".format(new_entry.course_code))
	
	except Exception as e:
		return(str(e))

#updating the skill table with all the skills
#add skills only if they dont exist in the skill table	
@app.route('/PostSkillDetail/', methods=['POST']) 
def create_skill():

	try:
		if 'skill_name' not in request.json or 'skill_type' not in request.json:
			return ("skill_name and skill_type must be included in the request")
		elif type(request.json["skill_name"]) != str or type(request.json["skill_type"]) != str:
			return ("skill_name and skill_type need to be in string format")
		else:
			skill_name = request.json["skill_name"]
			skill_type = request.json["skill_type"]
		
		temp_list = ["Hard Skill","Soft Skill"]
		
		if skill_type not in temp_list:
			return("Skill_type only accepts values 'Hard Skill' or 'Soft Skill'")
		else:
			valid_skill_name = Skill.query.filter_by(skill_name=skill_name).first()

			if valid_skill_name is not None:
				return("The skill you are trying to add already exists")
			else:
				new_entry = Skill(skill_name=skill_name,skill_type=skill_type)
				db.session.add(new_entry)
				db.session.commit()
		
			return jsonify("{} has been added to the database".format(new_entry.skill_name))
	
	except Exception as e:
		return(str(e))

#skills refers to a list of skills
@app.route('/PostStudentRating/', methods=['POST']) 
def create_rating():

	try:
		ratee_email = request.json["ratee_email"]
		course_code = request.json["course_code"]
		skills = request.json["skills"]
		rater_email = request.json["rater_email"]

		for i in skills:
			valid_skill = Skill.query.filter_by(skill_name=i).first()
			if valid_skill is None:
				return("Skill does not exist in our database")

		valid_ratee = Student.query.filter_by(email=ratee_email).first()   #this is an object
		valid_rater = Student.query.filter_by(email=rater_email).first()

		if valid_ratee is None or valid_rater is None:
			return("Either the ratee or rater does not exist in our database")
		else:
			check1 = False
			check2 = False
			#list of courses in the student's profile is in the form of course codes
			#checking if bothe rater and ratee has taken the course
			for i in valid_ratee.courses:
				if i.course_code == course_code:
					check1 = True
					break

			for j in valid_rater.courses:
				if j.course_code == course_code:
					check2 = True
					break
			
			if check1 == True and check2 == True:
				for i in skills:
					skill = Skill.query.filter_by(skill_name=i).first()
					new_entry = Rating(ratee_id=valid_ratee.id,skill_id=skill.id,rater_id=valid_rater.id,course_code=course_code)
					db.session.add(new_entry)
					db.session.commit()

					# Refer to candidature_skill associative table 
					# For each student, there can only be unique skills under the skill_id column
					# eg. Shouldn't be adding more than 1 'leadership' for a person called 'John'
					if i not in valid_ratee.skills:
						valid_ratee.skills.append(skill)
						db.session.commit()

				return jsonify("Rating for {} has been recorded".format(valid_ratee.email))
			else:
				return("Both rater and ratee must take the same course")
	
	except Exception as e:
		return(str(e))

@app.route('/GetSearchStudent/', methods=['POST']) 
def search_student():
	if 'email' not in request.args:
		return 'Email of the student must be included in the request'
	elif type(request.args['email']) != str:
		return 'Email must be typed in a string format.'
	else:
		searched_student = Student.query.filter_by(email=email).first()
		if searched_student is None:
			return 'The student you searched does not exist in the RateMe system.'
		return jsonify ([searched_student.serialize()])

# your code ends here 

if __name__ == '__main__':
	app.run(debug=True)
