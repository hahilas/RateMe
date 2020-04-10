import requests
#import json

base_url = 'http://127.0.0.1:5000/'
createstudent_url = base_url + 'student/'
createcourse_url = base_url + 'course/'
createskill_url = base_url + 'skill/'
updatestudentcourse_url = base_url + 'studentcourse/'

stud_list = [] #fill in these with nested list of student details in the format (email,fullname,courses)
course_list = [] #fill in these with nested list of course_details in the format (course_code, course_name)
skill_list = [] # fill in these with nested list of skill_details in the format (skill_name, skill_type)
email_list = [] #fill list of email addresses to search

def test_createstudent(email,fullname,courses):
    json = {'email':email,'fullname':fullname, 'courses':courses}
    r = requests.post(createstudent_url, json=json)
    print(r.status_code)
    print(r.text)

def test_createcourse(course_code,course_name):
    json = {'course_code':course_code,'course_name':course_name}
    r=requests.post(createcourse_url, json=json)
    print(r.status_code)
    print(r.text)

def test_createskill(skill_name,skill_type):
    json = {'skill_name':skill_name, 'skill_type':skill_type}
    r = requests.post(createskill_url, json=json)
    print(r.status_code)
    print(r.text)

def test_updatestudent(email, course_codes):
    json = {'email':email, 'course_codes':course_codes}
    r = requests.put(updatestudentcourse_url, json=json)
    print(r.status_code)
    print(r.text)


def test_readstudent(email):
    params = {'email': email}
    r = requests.get(readstudent_url, params=params).json()
    print(r.status_code)
    print(r.text)

#test_createstudent("siti@gmail.com","abc123",["SMT202"])

#test_createskill("Hardworking","Soft Skills")

#test_createcourse("SMT2O1","Geographic Info System for Urban Planning")

test_updatestudent("siti@gmail.com",["SMT202"])

# for i in stud_list:
#     test_createstudent(i[0],i[1],[i[2]])

# for i in course_list:
#     test_createcourse(i[0],i[1])

# for i in skill_list:
#     test_createskill(i[0],i[1])

# for i in email_list:
#     test_readstudent(i)
