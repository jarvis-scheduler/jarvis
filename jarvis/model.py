from collections import namedtuple

Department = namedtuple('Department', ['department_id', 'name'])

Result = namedtuple('Result', ['rating', 'schedule'])
Course = namedtuple('Course', ['crn', 'course', 'title', 'meetings'])
Meeting = namedtuple('Meeting', ['time', 'days', 'instructor', 'location', 'type'])

MeetingTime = namedtuple('MeetingTime', ['hours', 'minutes'])
MeetingRange = namedtuple('MeetingRange', ['start', 'end'])

Instructor = namedtuple('Instructor', ['first_name', 'last_name', 'rating'])
Rating = namedtuple('Rating', ['score', 'rating_id'])
