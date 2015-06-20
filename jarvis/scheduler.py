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
                start.append(time_range.start.hours*100 + time_range.start.minutes)
                end.append(time_range.end.hours * 100 + time_range.end.minutes)
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
        for meeting_rect in itertools.product(meeting.days, [meeting.time]):
            meetings_rect.append(meeting_rect)
    return meetings_rect


def scheduler(requirements):
    course_text = ""
    for course in requirements:
        course_text += course[0].course + ", "
    course_text = course_text[:-2]
    print("Finding courses for: %s" % course_text)
    print()
    all_schedules = get_schedules(requirements)
    print("Possible permutations: %d" % len(all_schedules))

    possible = []

    for schedule in all_schedules:
        schedule = Result(0, schedule)
        rating_counter = 0
        meetings = []
        for class_data in schedule.schedule:
            for meeting in class_data.meetings:
                if meeting.instructor.rating != 'unknown' and meeting.instructor.rating.score != 'unknown':
                    rating_counter += 1
                    schedule = schedule._replace(rating=schedule.rating + meeting.instructor.rating.score)
                meetings.append(meeting)

        schedule = schedule._replace(rating=(schedule.rating / (rating_counter * 5 / 100)))

        meetings_rect = expand_meetings(meetings)
        if is_possible(meetings_rect):
            possible.append(schedule)

    print("%d solutions found" % len(possible))

    possible.sort(key=lambda x: x.rating, reverse=True)

    return possible[:20]
