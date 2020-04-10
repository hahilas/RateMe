# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import threading
import os
import requests 
import json
import time

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# # Step 03: add database configurations here

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Student, Course, Skill, Rating, Rate_Detail, States
chat_id = 0 # fill in your chat id here
api_token = ' ' # fill in your api token here 
rm_url = 'https://smtrmpp.herokuapp.com//'
base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
sendMsg_url = base_url + 'sendMessage'
sendPhoto_url = base_url + 'sendPhoto'
rm_search = rm_url + 'student/'
rm_createrate = rm_url +'rating/'
rm_state = rm_url +'state/'
rm_skill = rm_url + 'skill/'
photo_url = 'https://imgur.com/a/LbYYJtn'

# Step 05: add routes and their binded functions here
def parse_message(message):
	chat_id = message['message']['chat']['id']
	txt = message['message']['text']
	
	return chat_id, txt

def send_photo(chat_id,photo_url):
	some_params={'chat_id':chat_id, 'photo':photo_url}
	r=requests.post(sendPhoto_url, params=some_params)


def send_message(chat_id,msg_text):
	some_params ={'chat_id':chat_id, 'text':msg_text, 'parse_mode':'HTML'}
	r = requests.post(sendMsg_url, params=some_params)


def rate_or_search(chat_id):

  keyboard_button = [[{'text':"Rate a Student"}], [{'text':"Search for a Student"}]]
  custom_keyboard = {'keyboard':keyboard_button, 'one_time_keyboard':True}
  reply_markup = json.JSONEncoder().encode(custom_keyboard) #encode in json format
  some_params = {'chat_id': chat_id , 'text':'Hello! Would you like to rate or search for a student?', 'reply_markup': reply_markup} #https://core.telegram.org/bots/api#sendmessage
  requests.post(sendMsg_url, some_params)


def search_stud(chat_id,txt,status):
	m = "Please enter the email of the student (e.g. mary.lim.2018@sis.smu.edu.sg). If you would like to stop searching, please type /exit"
	m1 = "User not found, Please try again with a valid email. If you would like to stop searching, please type /exit"
	m2 = "Thanks for using RateMe"
	m3 = ''
	m4 = ''
	rating_dict = {}
	counter = 0


	if status == 'keying in input' and txt != '/exit':
		query_url = rm_search + txt
		r = requests.get(query_url)
		if len(r.json()) == 0:
			send_message(chat_id,m1)
			return(status)
		else:
			stud_name = r.json()['fullname']
			for i in r.json()['rating']:
				counter += 1
				for i in i['rate_details']:
					if i['skill'] not in rating_dict:
						rating_dict[i['skill']] = 1
					else:
						rating_dict[i['skill']] += 1

			for keys in rating_dict:
				m3 += '<strong>{}</strong> : {} \n'.format(keys,rating_dict[keys])
			m4 = '<strong>{}</strong> has been rated <u>{}</u> times for the following skills: \n\n'.format(stud_name,counter) + m3
			send_message(chat_id,m4)
			status ='done'
			return status


	if status == 'keying in input' and txt == '/exit':
		send_message(chat_id,m2)
		status = 'done'
		return status

	if status == 'nil':
		send_message(chat_id,m)
		status = 'keying in input'
		return (status)
	
def rate_student(chat_id,txt,status):
	m = "Please enter the email of the student (E.g. mary.lim.2018@sis.smu.edu.sg). Feel free to type /exit to stop at anytime"
	m1 = "Please enter the course code both of you have taken together"
	m2 = "Please enter at most 3 skills your group mate has displayed from the list above in this format (Case Sensitive): skill 1, skill 2, skill 3"
	m3 = "Please enter your email so we can keep track of our raters"
	m4 = "Please try again. " + m
	m5 = "Thanks for using RateMe"

	query_url1= rm_state + str(chat_id)
	r = requests.get(query_url1)
	holder = {'chat_id':r.json()['chat_id'],'stage':r.json()['stage'],'ratee_email':r.json()['ratee_email'],'course_code':r.json()['course_code'],'skills':r.json()['rate_skill1'],'rater_email':r.json()['rater_email1']}

	if txt == '/exit':
		send_message(chat_id,m5)
		status = 'done2'
		return (status)

	if status == 'keying in rate input own email':
		holder['rater_email'] = txt
		k = requests.put(rm_state, json=holder)
		r = requests.get(query_url1)
		c = str(r.json()['rate_skill1'])
		print(c)
		d = ''
		for i in range(1,len(c)-1):
			n = c[i].lstrip('{').rstrip('}')
			b = n.lstrip("'").rstrip("'")
			x = b.lstrip('"').rstrip('"')
			d += x
		e = list(d.split(','))
		f = str(r.json()['ratee_email']).lstrip('{').rstrip('}')
		g = str(r.json()['course_code']).lstrip('{').rstrip('}')
		h = str(r.json()['rater_email1']).lstrip('{').rstrip('}')
		print(e,f,g,h)
		json_params = {'ratee_email':f,'course_code':g,'skills':e,'rater_email':h}
		r = requests.post(rm_createrate,json=json_params)
		if r.status_code == 200:
			send_message(chat_id,r.text)
			status = 'done2'
			return(status)
		else:
			send_message(chat_id,r.text)
			send_message(chat_id,m4)
			holder = {'chat_id':chat_id,'stage':'nil','ratee_email':'d','course_code':'d','skills':'d','rater_email':'d'}
			k = requests.put(rm_state, json=holder)
			status = 'keying in rate input email'
			return(status)

	if status == 'keying in rate input email':
		holder['ratee_email'] = txt
		send_message(chat_id,m1)
		status = 'keying in rate input course'
		return (status)
	
	if status == 'keying in rate input course':
		holder['course_code'] = txt
		send_photo(chat_id,photo_url)
		send_message(chat_id,m2)
		status = 'keying in rate input skill'
		return (status)
	
	if status == 'keying in rate input skill':
		holder['skills'] = txt
		send_message(chat_id,m3)
		status = 'keying in rate input own email'
		return (status)

	if status == 'nil':
		send_message(chat_id,m)
		status = 'keying in rate input email'
		return (status)
	
	return(status)


def listen_and_reply(chat_id,txt,status):
	print(chat_id,txt,status)
	if txt == '/start':
		rate_or_search(chat_id)
		status = 'nil'
		return status
	elif txt =='Search for a Student':
		a=search_stud(chat_id,txt,status)
		return a
	elif status == 'keying in input':
		a=search_stud(chat_id,txt,status)
		return a
	elif txt == 'Rate a Student' or status == 'keying in rate input email' or status == 'keying in rate input own email' or status == 'keying in rate input skill' or status == 'keying in rate input course':
		a=rate_student(chat_id,txt,status)
		return a
	else:
		return ('nil')

def next_step(msg,chat_id,txt):
	query_url1= rm_state + str(chat_id)
	r = requests.get(query_url1)
	if len(r.json()) == 0:
		holder = {'chat_id':chat_id,'stage':'nil','ratee_email':'d','course_code':'d','skills':'d','rater_email':'d'}
		j = requests.post(rm_state, json=holder)
		if j.status_code == 200:
			resp = listen_and_reply(chat_id,txt,'nil')
			if resp != None:
				holder['stage'] = resp
				k = requests.put(rm_state, json=holder)
			else:
				holder['stage'] = 'nil'
				k = requests.put(rm_state, json=holder)
	else:
		a = r.json()['stage']
		resp = listen_and_reply(chat_id,txt,a)

		holder ={'chat_id':r.json()['chat_id'],'stage':r.json()['stage'],'ratee_email':r.json()['ratee_email'],'course_code':r.json()['course_code'],'skills':r.json()['rate_skill1'],'rater_email':r.json()['rater_email1']}
		if resp == 'keying in input':
			holder['stage'] = resp
			k = requests.put(rm_state, json=holder)

		if resp == 'done':
			holder['stage'] = 'nil'
			k = requests.put(rm_state, json=holder)
			
		if resp == 'keying in rate input email':
			holder['stage'] = resp
			k = requests.put(rm_state, json=holder)
			
		if resp == 'keying in rate input course':
			holder['stage'] = resp
			holder['ratee_email'] = txt
			k = requests.put(rm_state, json=holder)
			
		if resp == 'keying in rate input skill':
			holder['stage'] = resp
			holder['course_code'] = txt
			k = requests.put(rm_state, json=holder)
			
		if resp == 'keying in rate input own email':
			holder['stage'] = resp
			d= ''
			c = list(txt.split(','))
			for i in range(len(c)):
				c[i] = c[i].strip()
				d += c[i] + ','
			holder['skills'] = c
			k = requests.put(rm_state, json=holder)
			
		if resp == 'done2':
			holder = {'chat_id':chat_id,'stage':'nil','ratee_email':'d','course_code':'d','skills':'d','rater_email':'d'}
			k = requests.put(rm_state, json=holder)
	return
	


@app.route('/updates/', methods=['POST'])
def index():
	if request.method == 'POST':
		msg=request.get_json() 	
		chat_id, txt = parse_message(msg)
		a = threading.Thread(target=next_step, args=(msg,chat_id,txt))
		a.start()
		# query_url1= rm_state + str(chat_id)
		# r = requests.get(query_url1)
		# if len(r.json()) == 0:
		# 	holder = {'chat_id':chat_id,'stage':'nil','ratee_email':'d','course_code':'d','skills':'d','rater_email':'d'}
		# 	j = requests.post(rm_state, json=holder)
		# 	if j.status_code == 200:
		# 		resp = listen_and_reply(chat_id,txt,'nil')
		# 		if resp != None:
		# 			holder['stage'] = resp
		# 			k = requests.put(rm_state, json=holder)
		# 		else:
		# 			holder['stage'] = 'nil'
		# 			k = requests.put(rm_state, json=holder)
		# else:
		# 	a = r.json()['stage']
		# 	resp = listen_and_reply(chat_id,txt,a)

		# 	holder ={'chat_id':r.json()['chat_id'],'stage':r.json()['stage'],'ratee_email':r.json()['ratee_email'],'course_code':r.json()['course_code'],'skills':r.json()['rate_skill1'],'rater_email':r.json()['rater_email1']}
		# 	if resp == 'keying in input':
		# 		holder['stage'] = resp
		# 		k = requests.put(rm_state, json=holder)

		# 	if resp == 'done':
		# 		holder['stage'] = 'nil'
		# 		k = requests.put(rm_state, json=holder)
			
		# 	if resp == 'keying in rate input email':
		# 		holder['stage'] = resp
		# 		k = requests.put(rm_state, json=holder)
			
		# 	if resp == 'keying in rate input course':
		# 		holder['stage'] = resp
		# 		holder['ratee_email'] = txt
		# 		k = requests.put(rm_state, json=holder)
			
		# 	if resp == 'keying in rate input skill':
		# 		holder['stage'] = resp
		# 		holder['course_code'] = txt
		# 		k = requests.put(rm_state, json=holder)
			
		# 	if resp == 'keying in rate input own email':
		# 		holder['stage'] = resp
		# 		d= ''
		# 		c = list(txt.split(','))
		# 		for i in range(len(c)):
		# 			c[i] = c[i].strip()
		# 			d += c[i] + ','
		# 		holder['skills'] = c
		# 		k = requests.put(rm_state, json=holder)
			
		# 	if resp == 'done2':
		# 		holder = {'chat_id':chat_id,'stage':'nil','ratee_email':'d','course_code':'d','skills':'d','rater_email':'d'}
		# 		k = requests.put(rm_state, json=holder)
	

		return Response('Ok', status=200)

@app.route('/state/', methods=['POST'])
def state_fc():
	chatid = request.json['chat_id']
	stage = request.json['stage']
	ratee_email = request.json['ratee_email']
	course_code = request.json['course_code']
	skills = request.json['skills']
	rater_email = request.json['rater_email']

	valid_chatid = States.query.filter_by(chatid=chatid).first()

	if valid_chatid is None:
		new_entry = States(chatid=chatid,stage=stage,ratee_email1=ratee_email,course_code1=course_code,rate_skill1=skills,rater_email1=rater_email)
		db.session.add(new_entry)
		db.session.commit()

		return(jsonify('{} has been entered'.format(chatid)),200)
		
@app.route('/state/', defaults={'chatid':None})
@app.route('/state/<string:chatid>/', methods=['GET']) 
def state_fcs(chatid):

	try:
		if chatid is None:
			chatids = States.query.all()
			if chatids is None:
				return(jsonify([]),200)
			else:
				return (jsonify([i.serialize() for i in chatids]),200)
		else:
			chatids = States.query.filter_by(chatid=chatid).first()
			if chatids is None:
				return (jsonify([]),200)
			else:
				return (jsonify(chatids.serialize()),200)

	except Exception as e:
		return (str(e))

@app.route('/state/', methods=['PUT'])
def put_state():
	try:
		chatid = request.json['chat_id']
		stage = request.json['stage']
		ratee_email = request.json['ratee_email']
		course_code = request.json['course_code']
		skills = request.json['skills']
		rater_email = request.json['rater_email']
		valid_chatid = States.query.filter_by(chatid=chatid).first()

		if valid_chatid is not None:
			valid_chatid.stage = stage
			valid_chatid.ratee_email1 = ratee_email
			valid_chatid.course_code1= course_code
			valid_chatid.rate_skill1 = skills
			valid_chatid.rater_email1 = rater_email
			db.session.commit()

			return(jsonify('{} has been updated'.format(chatid)),200)

	except Exception as e:
		return(str(e))


@app.route('/student/', methods=['POST']) 
def create_student(): 

	try:
		if 'email' not in request.json or 'fullname' not in request.json or 'courses' not in request.json:
			return(jsonify("email,fullname and courses must be included in the request"),400)
		elif type(request.json['email']) != str or type(request.json['fullname']) != str or type(request.json['courses']) != list:
			return(jsonify("email and fullname to be in string format, courses in list format"),400)
		else:
			email = request.json["email"]
			fullname = request.json["fullname"]
			courses = request.json["courses"]

		valid_email = Student.query.filter_by(email=email).first()

		for i in courses:
			if type(i) != str:
				return (jsonify("Please ensure all the values in the list are in String format"),400)
			else:
				valid_course = Course.query.filter_by(course_code=i).first()
				if valid_course is None:
					return(jsonify("{} course does not exist".format(i)),400)

		if valid_email is not None:
			return(jsonify("User already exists in database"),400)
		else:
			new_entry = Student(email=email,fullname=fullname)
			db.session.add(new_entry)
			db.session.commit()

			for i in courses:
				valid_course = Course.query.filter_by(course_code=i).first()
				new_entry.courses.append(valid_course)
				db.session.commit()

			return (jsonify("{} has been added to the database".format(new_entry.email)),200)

	except Exception as e:
		return(str(e))

@app.route('/course/', methods=['POST']) 
def create_course():

	try:
		if 'course_code' not in request.json or 'course_name' not in request.json:
			return (jsonify("course_code and course_name must be included in the request"),400)
		elif type(request.json["course_code"]) != str or type(request.json["course_name"]) != str:
			return (jsonify("course_code and course_name need to be in string format"),400)
		else:
			course_code = request.json["course_code"]
			course_name = request.json["course_name"]

		valid_course_code = Course.query.filter_by(course_code=course_code).first()
		valid_course_name = Course.query.filter_by(course_name=course_name).first()

		if valid_course_code is not None or valid_course_name is not None:
			return(jsonify("The course code or course name you are trying to add already exists"),400)
		else:
			new_entry = Course(course_code=course_code,course_name=course_name)
			db.session.add(new_entry)
			db.session.commit()
		
		return (jsonify("{} has been added to the database".format(new_entry.course_code)),200)
	
	except Exception as e:
		return(str(e))
	
@app.route('/skill/', methods=['POST']) 
def create_skill():

	try:
		if 'skill_name' not in request.json or 'skill_type' not in request.json:
			return (jsonify("skill_name and skill_type must be included in the request"),400)
		elif type(request.json["skill_name"]) != str or type(request.json["skill_type"]) != str:
			return (jsonify("skill_name and skill_type need to be in string format"),400)
		else:
			skill_name = request.json["skill_name"]
			skill_type = request.json["skill_type"]
		
		temp_list = ["Hard skill","Soft skill"]
		
		if skill_type not in temp_list:
			return(jsonify("Skill_type only accepts values 'Hard skill' or 'Soft skill', case sensitive"),400)
		else:
			valid_skill_name = Skill.query.filter_by(skill_name=skill_name).first()

			if valid_skill_name is not None:
				return(jsonify("The skill you are trying to add already exists"),400)
			else:
				new_entry = Skill(skill_name=skill_name,skill_type=skill_type)
				db.session.add(new_entry)
				db.session.commit()
		
			return (jsonify("{} has been added to the database".format(new_entry.skill_name)),200)
	
	except Exception as e:
		return(str(e),400)

@app.route('/rating/', methods=['POST']) 
def create_rating():

	try:
		if 'ratee_email' not in request.json or 'course_code' not in request.json or 'skills' not in request.json or 'rater_email' not in request.json:
			return (jsonify('ratee_email, course_code, skills and rater_email must be included in the request'), 400)
		elif type(request.json['ratee_email']) != str or type(request.json['course_code']) != str or type(request.json['skills']) != list or type(request.json['rater_email']) != str:
			print(type(request.json['ratee_email']),type(request.json['course_code']),type(request.json['skills']),type(request.json['rater_email']))
			return (jsonify('ratee_email, course_code and rater_email should be in String format, skills in list format'),400)
		else:
			ratee_email = request.json["ratee_email"]
			course_code = request.json["course_code"]
			skills = request.json["skills"]
			rater_email = request.json["rater_email"]
		
		valid_course_code = Course.query.filter_by(course_code=course_code).first()
		if valid_course_code is None:
			return(jsonify('{} course does not exist in our database'.format(course_code)),400)

		for i in skills:
			if type(i) != str:
				return (jsonify("Please ensure every value in the list is in string format"),400)
			else:
				valid_skill = Skill.query.filter_by(skill_name=i).first()
				if valid_skill is None:
					return(jsonify("{} skill does not exist in our database".format(i)),400)

		valid_ratee = Student.query.filter_by(email=ratee_email).first()
		valid_rater = Student.query.filter_by(email=rater_email).first()

		if valid_ratee is None or valid_rater is None:
			return(jsonify("Either the ratee or rater does not exist in our database"),400)
		else:
			if valid_ratee.id == valid_rater.id:
				return(jsonify("Rater and Ratee cannot be the same person!"),400)
			
			check1 = False
			check2 = False

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
					valid_rate = Rate_Detail.query.filter(Rate_Detail.skill_id == skill.id).filter(Rate_Detail.rater_id == valid_rater.id).filter(Rate_Detail.ratee_id ==valid_ratee.id).first()
					if valid_rate is not None:
						return (jsonify('You have rated {} for {} before'.format(i,valid_ratee.fullname)),400)

				new_entry1 = Rating(ratee_id=valid_ratee.id)
				db.session.add(new_entry1)
				db.session.commit()

				for i in skills:
					skill = Skill.query.filter_by(skill_name=i).first()
					new_entry = Rate_Detail(ratee_id=valid_ratee.id,skill_id=skill.id,rater_id=valid_rater.id,course_code=course_code,rate_id=new_entry1.id)
					db.session.add(new_entry)
					db.session.commit()

					if i not in valid_ratee.skills:
						valid_ratee.skills.append(skill)
						db.session.commit()

				return (jsonify("Rating for {} has been recorded".format(valid_ratee.email)),200)
			else:
				return(jsonify("Both rater and ratee must take the same course"),400)
	
	except Exception as e:
		return(str(e))

@app.route('/student/', defaults={'email':None})
@app.route('/student/<string:email>/', methods=['GET']) 
def search_student(email):
	try:
		if email is None:
			student = Student.query.all()
			return (jsonify([i.serialize() for i in student]),200)
		else:
			student = Student.query.filter_by(email=email).first()
			if student is None:
				return jsonify([])
			else:
				return (jsonify(student.serialize()),200)

	except Exception as e:
		return (str(e))

@app.route('/skill/', defaults={'skill':None})
@app.route('/skill/<string:skill>/', methods=['GET']) 
def get_skill(skill):
	try:
		if skill is None:
			skills = Skill.query.all()
			return (jsonify([i.serialize() for i in skills]),200)
		else:
			skills = Skill.query.filter_by(skill_name=skill).first()
			if skills is None:
				return (jsonify([]),200)
			else:
				return (jsonify(skills.serialize()),200)

	except Exception as e:
		return (str(e))

@app.route('/course/', defaults={'course':None})
@app.route('/course/<string:course>/', methods=['GET']) 
def get_course(course):
	try:
		if course is None:
			courses = Course.query.all()
			return (jsonify([i.serialize() for i in courses]),200)
		else:
			courses = Course.query.filter_by(course_code=course).first()
			if courses is None:
				return (jsonify([]),200)
			else:
				return (jsonify(courses.serialize()),200)
	except Exception as e:
		return (str(e))

@app.route('/student/', methods=['PUT'])
def update_student():
	try:
		if 'email' not in request.json or 'courses' not in request.json:
			return(jsonify("email and courses must be in the parameters"),400)
		elif type(request.json['email']) != str or type(request.json['courses']) != list:
			return(jsonify('email must be in string format and course must be in list format'),400)
		else:
			email = request.json['email']
			courses = request.json['courses']

		student = Student.query.filter_by(email=email).first()

		temp_holder = []

		for i in courses:
			valid_course = Course.query.filter_by(course_code=i).first()
			if valid_course is None:
				return(jsonify("Course does not exist in our database"),400)
			else:
				temp_holder.append(valid_course)
		
		if student is None:
			return(jsonify('Email does not exist in our database'),400)
		else:
			student.courses = temp_holder
			db.session.commit()
			return (jsonify(student.serialize()),200)
			
	except Exception as e:
		return(str(e))

@app.route('/ratedet/', methods=['GET'])
def get_ratedet():
	try:
		ratedets = Rate_Detail.query.all()
		return (jsonify([i.serialize() for i in ratedets]),200)

	except Exception as e:
		return (str(e))

#######
#work in prog
#######
# @app.route('/skillcount2/', defaults={'skill':None})
# @app.route('/skillcount2/<string:skill>/',methods=['GET'])
# def get_skillcount2(skill):
# 	try:
# 		if skill is None:
# 			skill_count = {}
# 			r = requests.get(rm_skill)
# 			for i in r.json():
# 				skill_count[i['skill_name']] = 0
			



@app.route('/skillcount/', defaults={'skill':None})
@app.route('/skillcount/<string:skill>/',methods=['GET'])
def get_skillcount(skill):
	try:
		if skill is None:
			skill_count = {}
			count = 0
			for x in range(75,121):
				req_skill = Skill.query.filter_by(id = x).first()
				req_skill_name = req_skill.skill_name
				
				if Rate_Detail.query.filter_by(skill_id=x).first() is not None:
					all_req_rating = Rate_Detail.query.filter_by(skill_id = x).all()
					for i in all_req_rating:
						count+=1
				else:
					count = 0
				skill_count[req_skill_name]=count
				
		else:
			skill_check = Skill.query.filter_by(skill_name=skill).first()
			if skill_check is None:
				return "There is no such skill in the RateMe database."
			else:
				skill_count={}
				count=0
				req_skill = Skill.query.filter_by(skill_name=skill).first()
				req_skill_id = req_skill.id
				all_req_rating = Rate_Detail.query.filter_by(skill_id = req_skill.id).all()
				for i in all_req_rating:
					count+=1
				skill_count[skill]=count
		return skill_count
	except Exception as e:
		return (str(e))




# your code ends here 

if __name__ == '__main__':
	app.run(port=5000, debug=True)
