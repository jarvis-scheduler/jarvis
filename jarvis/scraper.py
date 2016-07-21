from multiprocessing import Pool
import os
import os.path
import pickle
import re

from pyquery import PyQuery as pq
import requests
from jarvis.model import *

p = re.compile('\s.\.')

COURSES_SCHEDULE = 'https://www.deanza.edu/schedule/classes/index.html'
COURSES_SEARCH = 'https://www.deanza.edu/schedule/classes/schsearch.html'

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

YEAR = str(2016)

quarter = YEAR + QUARTER_MAPPING['fall']


def get_departments():
    print('Downloading departments list...')
    search_page = pq(requests.get(COURSES_SCHEDULE).text)
    department_options = search_page('#Uniq_Course_ID').items('option')
    departments = {
        Department(department_id=option.val(), name=option.text())
        for option in department_options if option.text() != ''
    }
    print('Found %s departments' % len(departments))
    return departments


def row_describes_course(row):
    return row('.snews').eq(2)('a')


def get_meeting_days(days_text):
    days = set()
    if days_text != 'TBA':
        days_text_split = []
        # don't kill me for this please
        i = 0
        days_text_len = len(days_text)
        while i < days_text_len:
            if days_text[i] in ['M', 'W', 'F', 'S']:
                days_text_split.append(days_text[i])
                i += 1
            else:
                if (i + 1) < days_text_len and days_text[i + 1] == 'h':
                    days_text_split.append('Th')
                    i += 2
                else:
                    days_text_split.append('T')
                    i += 1
        for day_key, day in DAYS_MAPPING:
            if day_key in days_text_split:
                days.add(day)
    return days

def get_meeting_instructor(instructor_text):
    comma_index = instructor_text.find(',')

    last_name = instructor_text[:comma_index].capitalize()
    first_name = instructor_text[comma_index + 1:].strip().capitalize()

    middle_match = p.search(first_name)
    if not middle_match == None:
        print(middle_match.group())
        first_name = first_name[:middle_match.start()]

    return Instructor(first_name=first_name, last_name=last_name, rating='unknown')


def get_meeting_type(type_text):
    return TYPES_MAPPING[type_text]


def get_time(time_text):
    colon_index = time_text.find(':')
    space_index = time_text.find(' ')
    hours = int(time_text[:colon_index])
    minutes = int(time_text[colon_index + 1:space_index])
    period = time_text[space_index + 1:]
    if period == 'PM' and hours < 12: hours += 12
    if period == 'AM' and hours == 12: hours = 0
    return MeetingTime(hours=hours, minutes=minutes)


def get_meeting_range(range_text):
    if '-' in range_text:
        [start, end] = [get_time(time_text) for time_text in range_text.split('-')]
        return MeetingRange(start=start, end=end)
    else:
        return 'TBA'


def get_course_info(row):
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
    meeting_type = get_meeting_type(meeting_title[opening_paren_index + 1:closing_paren_index])

    meeting = Meeting(time=meeting_time, days=meeting_days, instructor=meeting_instructor,
                      location=meeting_location, type=meeting_type)

    return Course(crn=crn, course=course, title=title, meetings=[meeting])


def get_meeting_info(row):
    snews = row('.snews')

    time = get_meeting_range(snews.eq(2).text())
    days = get_meeting_days(snews.eq(3).text())
    instructor = get_meeting_instructor(snews.eq(4).text())
    location = snews.eq(5).text()
    meeting_type = get_meeting_type(snews.eq(1).text()[1:-1])

    return Meeting(time=time, days=days, instructor=instructor, location=location, type=meeting_type)


def get_courses(department):
    headers = {
        'Referer': COURSES_SCHEDULE
    }
    payload = {
        'Quarter': quarter,
        'Uniq_Course_ID': department.department_id,
    }
    courses_page = pq(requests.post(COURSES_SEARCH, headers=headers, data=payload).text)
    courses_table = courses_page('.anti_nav_print_adj').eq(2)
    courses_rows = [row for row in courses_table.items('tr') if not row('hr') and row('.snews')]
    courses_computed = []
    for row in courses_rows:
        if row_describes_course(row):
            courses_computed.append(get_course_info(row))
        else:
            courses_computed[-1].meetings.append(get_meeting_info(row))
    courses_count_computed = len(courses_computed)
    print('Found %s courses for department %s' % (courses_count_computed, department.name))
    return courses_computed


def find_instructor_rating(instructor):
    human_name = '%s %s' % (instructor.first_name, instructor.last_name)
    if instructor.first_name == 'M' and instructor.last_name == 'Staff':
        print('Skipping instructor %s' % human_name)
        return instructor
    search_query = '%s %s De Anza College ' % (instructor.first_name, instructor.last_name)
    payload = {
        'query': search_query
    }

    search_page = pq(requests.get(RATING_SEARCH, params=payload).text)
    results = [result.attr('href') for result in search_page('.listings').items('.listing a')]
    if len(results) == 0:
        print('No rating found for instructor %s' % human_name)
        return instructor
    else:
        print('Rating found for instructor %s' % human_name)
        result = results[0]
        rating_id = result[result.find('=') + 1:]
        return get_instructor_rating(instructor, rating_id)


def get_instructor_rating(instructor, rating_id):
    payload = {
        'tid': rating_id
    }
    rating_page = pq(requests.get(RATING_SHOW, params=payload).text)
    rating = rating_page('.breakdown-header .grade').eq(0)
    if rating:
        return instructor._replace(rating=Rating(score=float(rating.text()), rating_id=rating_id))
    else:
        return instructor._replace(rating=Rating(score="unknown", rating_id=rating_id))


def instructor_id(instructor):
    return "%s %s" % (instructor.first_name, instructor.last_name)


def scrape():
    departments = get_departments()
    print('Downloading course information...')
    p = Pool(8)
    courses = [course for department_courses in p.map(get_courses, departments) for course in department_courses]
    instructors = set(
        meeting.instructor for course in courses for meeting in course.meetings
    )

    print('Found %s total courses' % len(courses))

    print('Downloading instructor rating information...')
    instructors = p.map(find_instructor_rating, instructors)

    print('Updating instructor data within courses..')
    instructors_map = {instructor_id(instructor): instructor for instructor in instructors}

    courses = [
        course._replace(meetings=[
            meeting._replace(instructor=instructors_map[instructor_id(meeting.instructor)])
            for meeting in course.meetings
        ]) for course in courses
    ]

    if not os.path.exists('data/'):
        os.mkdir('data/')

    print('Pickling department data...')
    with open('data/departments.pickle', 'wb') as departments_file:
        pickle.dump(departments, departments_file)

    print('Pickling course data...')
    with open('data/courses.pickle', 'wb') as courses_file:
        pickle.dump(courses, courses_file)

    print('Pickling instructor data...')
    with open('data/instructors.pickle', 'wb') as instructors_file:
        pickle.dump(instructors, instructors_file)

    print('Done')
