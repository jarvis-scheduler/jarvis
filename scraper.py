from pyquery import PyQuery as pq
import json
import requests

CLASSES_SCHEDULE = 'https://www.deanza.edu/schedule/classes/index.html'
CLASSES_SEARCH = 'https://www.deanza.edu/schedule/classes/schsearch.html'

def get_departments_list():
  print "Downloading departments list..."
  search_page = pq(requests.get(CLASSES_SCHEDULE).text)
  department_options = search_page('#Uniq_Course_ID').items('option')
  departments = {option.val(): option.text() for option in department_options if option.text() != ''}
  print "Found %s departments" % len(departments)
  return departments

def department_classes_request(department_id):

  # curl 'https://www.deanza.edu/schedule/classes/schsearch.html' 
  # -H 'Referer: https://www.deanza.edu/schedule/classes/index.html' 
  # --data 'QuarterQtr=M&QuarterYear=2015&sortBy=1&Quarter=2015M&Uniq_Course_ID=MATH&CourseID=&CourseTitle=&Instructor=&Location='

  headers = {
    'Referer': CLASSES_SCHEDULE
  }

  payload = {
    'QuarterQtr': 'M',
    'QuarterYear': '2015',
    'sortBy': '1',
    'Quarter': '2015M',
    'Uniq_Course_ID': department_id,
    'CourseID': '',
    'CourseTitle': '',
    'Instructor': '',
    'Location': ''
  }

  return requests.post(CLASSES_SEARCH, headers=headers, data=payload)

def get_classes_for_department(department_id, department_name):
  print "Downloading classes for department %s" % department_name
  classes_page = pq(department_classes_request(department_id).text)
  print classes_page('.snews').text()
  #print [elem('.snews') for elem in classes_page("anti_nav_print_adj").items("tr")]

departments = get_departments_list()

print "Downloading class information..."
for department_id in departments:
  get_classes_for_department(department_id, departments[department_id])