import requests

base_url = 'http://127.0.0.1:5000/'
create_url = base_url + 'PostStudentDetail/'
create2_url = base_url + 'PostCourseDetail/'
create3_url = base_url + 'PostSkillDetail/'

stud_list = [["salihahmr.2018@sis.smu.edu.sg","Siti Salihah",["SMT203","SMT202"]]] #fill in these with nested list of student details in the format (email,fullname,courses)
course_list = [] #fill in these with nested list of course_details in the format (course_code, course_name)
skill_list = [] # fill in these with nested list of skill_details in the format (skill_name, skill_type)

def test_create(email,fullname,courses):
    json = {'email':email,'fullname':fullname, 'courses':courses}
    r = requests.post(create_url, json=json)
    print(r.status_code)
    print(r.text)

def test_create2(course_code,course_name):
    json = {'course_code':course_code,'course_name':course_name}
    r=requests.post(create2_url, json=json)
    print(r.status_code)
    print(r.text)

def test_create3(skill_name,skill_type):
    json = {'skill_name':skill_name, 'skill_type':skill_type}
    r = requests.post(create3_url, json=json)
    print(r.status_code)
    print(r.text)


for i in stud_list:
    test_create(i[0],i[1],i[2])

# for i in course_list:
#     test_create2(i[0],i[1])

# for i in skill_list:
#     test_create3(i[0],i[1])