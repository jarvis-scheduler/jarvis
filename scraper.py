from pyquery import PyQuery as pq
from collections import namedtuple
import pprint
import json
import requests

CLASSES_SCHEDULE = 'https://www.deanza.edu/schedule/classes/index.html'
CLASSES_SEARCH = 'https://www.deanza.edu/schedule/classes/schsearch.html'

# guessed, but probably true?
QUARTER_MAPPING = {
  'winter': 'W',
  'spring': 'S',
  'summer': 'M',
  'fall': 'F'
}

# definitely true
DAYS_MAPPING = {
  'M': 'Monday',
  'T': 'Tuesday',
  'W': 'Wednesday',
  'Th': 'Thursday',
  'F': 'Friday',
  'S': 'Saturday'
}

# so far
TYPES_MAPPING = {
  'CLAS': 'Class',
  'LAB': 'Lab'
}

YEAR = str(2015)

quarter = YEAR + QUARTER_MAPPING['summer']

def get_departments():
  print 'Downloading departments list...'
  search_page = pq(requests.get(CLASSES_SCHEDULE).text)
  department_options = search_page('#Uniq_Course_ID').items('option')
  departments = {option.val(): option.text() for option in department_options if option.text() != ''}
  print 'Found %s departments' % len(departments)
  return departments

def department_classes_request(department_id):

  # curl 'https://www.deanza.edu/schedule/classes/schsearch.html' 
  # -H 'Referer: https://www.deanza.edu/schedule/classes/index.html' 
  # --data 'QuarterQtr=M&QuarterYear=2015&sortBy=1&Quarter=2015M&Uniq_Course_ID=MATH&CourseID=&CourseTitle=&Instructor=&Location='

  headers = {
    'Referer': CLASSES_SCHEDULE
  }

  payload = {
    'Quarter': quarter,
    'Uniq_Course_ID': department_id,
  }

  return requests.post(CLASSES_SEARCH, headers=headers, data=payload)

ClassSection = namedtuple('ClassSection', ['crn', 'course', 'title', 'meetings'])
ClassMeeting = namedtuple('ClassMeeting', ['time', 'days', 'instructor', 'location', 'type'])

Instructor = namedtuple('Instructor', ['first_name', 'last_name'])

def describes_class(row):
  return row('.snews').eq(2)('a')

def get_meeting_days(days_text):
  days = set()
  for day_key in DAYS_MAPPING:
    if day_key in days_text:
      days.add(DAYS_MAPPING[day_key])
  return days

def get_meeting_instructor(instructor_text):

  comma_index = instructor_text.find(',')

  last_name = instructor_text[:comma_index].capitalize()
  first_name = instructor_text[comma_index+1:].strip().capitalize()

  return Instructor(first_name=first_name, last_name=last_name)

def get_meeting_type(type_text):
  return TYPES_MAPPING[type_text]

def get_meeting_time(time_text):
  pass

def get_class_info(row):
  snews = row('.snews')
  crn = int(snews.eq(0).text())
  course = snews.eq(1).text()

  meeting_title = snews.eq(2).text()

  opening_paren_index = meeting_title.rfind('(')
  closing_paren_index = meeting_title.rfind(')')

  title = meeting_title[:opening_paren_index].strip()

  meeting_time = snews.eq(3).text()
  meeting_days = get_meeting_days(snews.eq(4).text())
  meeting_instructor = get_meeting_instructor(snews.eq(5).text())
  meeting_location = snews.eq(6).text()
  meeting_type = get_meeting_type(meeting_title[opening_paren_index+1:closing_paren_index])

  meeting = ClassMeeting(time=meeting_time, days=meeting_days, instructor=meeting_instructor, 
    location=meeting_location, type=meeting_type)

  return ClassSection(crn=crn, course=course, title=title, meetings=[meeting])

def get_meeting_info(row):
  snews = row('.snews')
  
  time = snews.eq(2).text()
  days = get_meeting_days(snews.eq(3).text())
  instructor = get_meeting_instructor(snews.eq(4).text())
  location = snews.eq(5).text()
  type = get_meeting_type(snews.eq(1).text()[1:-1])

  return ClassMeeting(time=time, days=days, instructor=instructor, location=location, type=type)

def get_classes(department_id, department_name):
  print 'Downloading classes for department %s' % department_name
  classes_page = pq(department_classes_request(department_id).text)
  classes_table = classes_page('.anti_nav_print_adj').eq(2)
  classes_rows = [row for row in classes_table.items('tr') if not row('hr') and row('.snews')]
  classes = []
  for row in classes_rows:
    if describes_class(row):
      classes.append(get_class_info(row))
    else:
      classes[-1].meetings.append(get_meeting_info(row))
  pprint.pprint(classes)
  #print [elem.text() for elem in classes_rows]
  #print [elem('.snews') for elem in classes_page('anti_nav_print_adj').items('tr')]

departments = get_departments()

print 'Downloading class information...'
# for department_id in departments:
#   get_classes(department_id, departments[department_id])
department_id = 'MATH'
get_classes(department_id, departments[department_id])