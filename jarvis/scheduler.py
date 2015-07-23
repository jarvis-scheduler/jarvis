import itertools
from jarvis.model import *


def get_schedules(requirements):
    schedules = []
    for schedule in itertools.product(*requirements):
        schedules.append(schedule)
    return schedules


def is_possible(meetings_rect):
    meetings_by_days = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
        'Saturday': []
    }
    for meeting_rect in meetings_rect:
        meetings_by_days[meeting_rect[0]].append(meeting_rect[1])
    for day_str, day in meetings_by_days.items():
        start = []
        end = []
        for time_range in day:
            if time_range != 'TBA':
                start.append(time_range['start']['hours'] * 60 + time_range['start']['minutes'])
                end.append(time_range['end']['hours'] * 60 + time_range['end']['minutes'])
        start.sort()
        end.sort()
        counter = 0
        while len(start) > 0:
            if start[0] < end[0]:
                start.pop(0)
                counter += 1
            else:
                end.pop(0)
                counter -= 1
            if counter >= 2:
                return False
    return True


def expand_meetings(meetings):
    meetings_rect = []

    for meeting in meetings:
        for meeting_rect in itertools.product(meeting['days'], [meeting['time']]):
            meetings_rect.append(meeting_rect)
    return meetings_rect


def scheduler(requirements):
    course_text = ""
    for course in requirements:
        course_raw = course[0]['course']
        if len(course_raw) == 11:
            course_raw = course_raw[2:]
        course_text += course_raw + ", "
    course_text = course_text[:-4]
    print("Finding courses for: %s" % course_text)
    print()
    all_schedules = get_schedules(requirements)
    print("Possible permutations: %d" % len(all_schedules))

    possible = []

    for schedule in all_schedules:
        schedule = Result(0, schedule)
        rating_counter = 0
        counter = 0
        meetings = []
        for class_data in schedule.schedule:
            for meeting in class_data['meetings']:
                if meeting['instructor']['rating'] != 'unknown' and meeting['instructor']['rating']['score'] != 'unknown':
                    rating_counter += 1
                    schedule = schedule._replace(rating=schedule.rating + meeting['instructor']['rating']['score'])
                counter += 1
                meetings.append(meeting)
        if rating_counter == 0:
            rating_result = -1
        else:
            rating_result = schedule.rating / (rating_counter * 5 / 100) - ((1 - rating_counter / counter)* 30)
        schedule = schedule._replace(rating=(rating_result))

        meetings_rect = expand_meetings(meetings)
        if is_possible(meetings_rect):
            possible.append(schedule)

    print("%d solutions found" % len(possible))

    possible.sort(key=lambda x: x.rating, reverse=True)

    for key, possibility in enumerate(possible):
        if possibility.rating == -1:
            possible[key] = possibility._replace(rating=("unknown"))

    return possible[:20]
