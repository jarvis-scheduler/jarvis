from pyquery import PyQuery as pq
from collections import namedtuple
from multiprocessing import Pool
import pprint
import json
import requests
import os
import os.path

CLASSES_SCHEDULE = 'https://www.deanza.edu/schedule/classes/index.html'
CLASSES_SEARCH = 'https://www.deanza.edu/schedule/classes/schsearch.html'

RATING_SEARCH = 'http://www.ratemyprofessors.com/search.jsp'
RATING_SHOW = 'http://www.ratemyprofessors.com/ShowRatings.jsp'

# guessed, but probably true?
QUARTER_MAPPING = {
  'winter': 'W',
  'spring': 'S',
  'summer': 'M',
  'fall': 'F',
}

# definitely true
DAYS_MAPPING = [
  ('M', 'Monday'),
  ('T', 'Tuesday'),
  ('W', 'Wednesday'),
  ('Th', 'Thursday'),
  ('F', 'Friday'),
  ('S', 'Saturday'),
]

# so far
TYPES_MAPPING = {
  'CLAS': 'Class',
  'LAB': 'Lab',
  'TBA': 'TBA',
  'LEC': 'Lecture',
}

YEAR = str(2015)

quarter = YEAR + QUARTER_MAPPING['summer']

def get_departments():
  print('Downloading departments list...')
  search_page = pq(requests.get(CLASSES_SCHEDULE).text)
  department_options = search_page('#Uniq_Course_ID').items('option')
  departments = {option.val(): option.text() for option in department_options if option.text() != ''}
  print('Found %s departments' % len(departments))
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

Instructor = namedtuple('Instructor', ['first_name', 'last_name', 'rating', 'rating_id'])

def row_describes_class(row):
  return row('.snews').eq(2)('a')

def get_meeting_days(days_text):
  days = []
  for day_key, day in DAYS_MAPPING:
    if day_key in days_text:
      days.append(day)
  return days

instructors_set = set()

def get_meeting_instructor(instructor_text):

  comma_index = instructor_text.find(',')

  last_name = instructor_text[:comma_index].capitalize()
  first_name = instructor_text[comma_index+1:].strip().capitalize()

  # meh, mutability
  instructors_set.add(
    Instructor(first_name=first_name, last_name=last_name, rating='unkown', rating_id='unkown')
  )

  return dict(first_name=first_name, last_name=last_name)

def get_meeting_type(type_text):
  return TYPES_MAPPING[type_text]

def get_time(time_text):
  colon_index = time_text.find(':')
  space_index = time_text.find(' ')
  hours = int(time_text[:colon_index])
  minutes = int(time_text[colon_index+1:space_index])
  period = time_text[space_index+1:]
  if period == 'PM' and hours < 12: hours += 12
  if period == 'AM' and hours == 12: hours = 0
  return dict(hours=hours, minutes=minutes)

def get_meeting_range(range_text):
  if '-' in range_text:
    [start, end] = [get_time(time_text) for time_text in range_text.split('-')]
    return dict(start=start, end=end)
  else:
    return 'TBA'

def get_class_info(row):
  snews = row('.snews')
  crn = snews.eq(0).text()
  course = snews.eq(1).text()

  meeting_title = snews.eq(2).text()

  opening_paren_index = meeting_title.rfind('(')
  closing_paren_index = meeting_title.rfind(')')

  title = meeting_title[:opening_paren_index].strip()

  meeting_time = get_meeting_range(snews.eq(3).text())
  meeting_days = get_meeting_days(snews.eq(4).text())
  meeting_instructor = get_meeting_instructor(snews.eq(5).text())
  meeting_location = snews.eq(6).text()
  meeting_type = get_meeting_type(meeting_title[opening_paren_index+1:closing_paren_index])

  meeting = dict(time=meeting_time, days=meeting_days, instructor=meeting_instructor, 
    location=meeting_location, type=meeting_type)

  return dict(crn=crn, course=course, title=title, meetings=[meeting])

def get_meeting_info(row):
  snews = row('.snews')
  
  time = get_meeting_range(snews.eq(2).text())
  days = get_meeting_days(snews.eq(3).text())
  instructor = get_meeting_instructor(snews.eq(4).text())
  location = snews.eq(5).text()
  type = get_meeting_type(snews.eq(1).text()[1:-1])

  return dict(time=time, days=days, instructor=instructor, location=location, type=type)

departments = get_departments()

def get_classes(department_id):
  department_name=departments[department_id]
  #print('Downloading classes for department %s' % department_name)
  classes_page = pq(department_classes_request(department_id).text)
  classes_table = classes_page('.anti_nav_print_adj').eq(2)
  classes_rows = [row for row in classes_table.items('tr') if not row('hr') and row('.snews')]
  classes = []
  for row in classes_rows:
    if row_describes_class(row):
      classes.append(get_class_info(row))
    else:
      classes[-1]['meetings'].append(get_meeting_info(row))
  classes_count_computed = len(classes)
  print('Found %s classes for department %s' % (classes_count_computed, department_name))
  return classes

print('Downloading class information...')
classes = [clss for department_id in departments for clss in get_classes(department_id)]
print('Found %s total classes' % len(classes))

print('Dumping class data...')

if not os.path.exists('data/'):
  os.mkdir('data/')

with open('data/classes.json', 'w') as f:
  json.dump(classes, f, indent=2)

instructors = [instructor._asdict() for instructor in instructors_set]

def find_instructor_rating_info(instructor):
  human_name = '%s %s' % (instructor['first_name'], instructor['last_name'])
  if instructor['first_name'] == 'M' and instructor['last_name'] == 'Staff':
    print('Instructor %s skipped' % (human_name))
    return
  search_query = ' '.join([instructor['first_name'], instructor['last_name'], 'De', 'Anza', 'College'])
  payload = {
    'query': search_query
  }
  search_page = pq(requests.get(RATING_SEARCH, params=payload).text)
  results = [result.attr('href') for result in search_page('.listings').items('.listing a')]
  if len(results) == 0:
    print('No rating found for instructor %s' % human_name)
  else:
    print('Rating found for instructor %s' % human_name)
    result = results[0]
    rating_id = result[result.find('=')+1:]
    instructor['rating_id'] = rating_id
    get_instructor_rating(instructor, rating_id)

def get_instructor_rating(instructor, rating_id): 
  payload = {
    'tid': rating_id
  }
  rating_page = pq(requests.get(RATING_SHOW, params=payload).text)
  rating = rating_page('.breakdown-header .grade').eq(0)
  instructor['rating'] = rating.text()

print('Downloading instructor rating information...')
for instructor in instructors:
  find_instructor_rating_info(instructor)

print('Dumping instructor data...')
with open('data/instructors.json', 'w') as f:
  json.dump(instructors, f, indent=2)

print('Done')