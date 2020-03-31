import requests
import json

base_url = 'http://127.0.0.1:5000/'
createstudent_url = base_url + 'PostStudentDetail/'
createcourse_url = base_url + 'PostCourseDetail/'
createskill_url = base_url + 'PostSkillDetail/'
readstudent_url = base_url + 'GetSearchStudent/'

stud_list = [["salihahmr.2018@sis.smu.edu.sg","Siti Salihah",["SMT203","SMT202"]]] #fill in these with nested list of student details in the format (email,fullname,courses)
course_list = [] #fill in these with nested list of course_details in the format (course_code, course_name)
skill_list = [] # fill in these with nested list of skill_details in the format (skill_name, skill_type)
email_list = [] #fill list of email addresses to search

def test_createstudent(email,fullname,courses):
    json = {'email':email,'fullname':fullname, 'courses':courses}
    r = requests.post(create_url, json=json)
    print(r.status_code)
    print(r.text)

def test_createcourse(course_code,course_name):
    json = {'course_code':course_code,'course_name':course_name}
    r=requests.post(create2_url, json=json)
    print(r.status_code)
    print(r.text)

def test_createskill(skill_name,skill_type):
    json = {'skill_name':skill_name, 'skill_type':skill_type}
    r = requests.post(create3_url, json=json)
    print(r.status_code)
    print(r.text)

def test_readstudent(email):
    params = {'email': email}
    r = requests.get(readstudent_url, params=params).json()
    print(r.status_code)
    print(r.text)


for i in stud_list:
    test_createstudent(i[0],i[1],i[2])

# for i in course_list:
#     test_createcourse(i[0],i[1])

# for i in skill_list:
#     test_createskill(i[0],i[1])

# for i in email_list:
#     test_readstudent(i)
