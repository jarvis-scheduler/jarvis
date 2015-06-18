from pyquery import PyQuery as pq
from collections import namedtuple
import json
import requests

CLASSES_SCHEDULE = 'https://www.deanza.edu/schedule/classes/index.html'
CLASSES_SEARCH = 'https://www.deanza.edu/schedule/classes/schsearch.html'

def get_departments():
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
    'Quarter': '2015M',
    'Uniq_Course_ID': department_id,
  }

  return requests.post(CLASSES_SEARCH, headers=headers, data=payload)

ClassSection = namedtuple('ClassSection', ['crn', 'course', 'title', 'meetings'])
ClassMeeting = namedtuple('ClassMeeting', ['time', 'days', 'instructor', 'location', 'type'])

def get_classes(department_id, department_name):
  print "Downloading classes for department %s" % department_name
  classes_page = pq(department_classes_request(department_id).text)
  classes_table = classes_page('.anti_nav_print_adj').eq(2)
  classes_rows = list(classes_table.items('tr'))[3:]
  print [elem.text() for elem in classes_rows]
  #print [elem('.snews') for elem in classes_page("anti_nav_print_adj").items("tr")]

departments = get_departments()

print "Downloading class information..."
# for department_id in departments:
#   get_classes(department_id, departments[department_id])
department_id = 'MATH'
get_classes(department_id, departments[department_id])