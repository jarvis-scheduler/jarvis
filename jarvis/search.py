from jarvis.model import *
from collections import defaultdict
import pickle
import re


def preprocess_index():
    index = {}
    with open('data/courses.pickle', 'rb') as courses_file:
        courses = pickle.load(courses_file)

    for course in courses:
        data_str = '%s %s %s' % (course.crn, course.title, course.course)
        for meeting in course.meetings:
            instructor_name = '%s %s' % (meeting.instructor.first_name,
                                         meeting.instructor.last_name)
            if instructor_name not in data_str:
                data_str += " " + instructor_name
        index[data_str] = course
    with open('data/index.pickle', 'wb') as index_file:
        pickle.dump(index, index_file)

def search(search, class_types):
    search = search.lower()

    index_map = {"hybrid": '*',
                 "communities": '+',
                 "community-service": '^',
                 "offcampus": '#'}

    index_set = {index_map[class_type] for class_type in set(class_types)}

    with open('data/index.pickle', 'rb') as index_file:
        index = pickle.load(index_file)

    split = search.split()
    matches_list = []
    for x in range(len(split)):
        matches_raw = [v for (k, v) in index.items() if split[x] in k.lower()]
        if not x == 0:
            matches_list = [i for i in matches_list if i in matches_raw]
        else:
            matches_list = matches_raw
    matches = defaultdict(list)
    regex = re.compile(r"-0*")
    for match in matches_list:
        if match.course[0] in index_set:
            if match.course[10] == '.':
                match_key = match.course[2:10]
                match_key = regex.sub(" ", match_key)
                matches[match_key].append(match)
            else:
                match_key = match.course[2:11]
                match_key = regex.sub(" ", match_key)
                matches[match_key].append(match)
        elif match.course[0] not in set(index_map.values()) ^ index_set:
            if match.course[8] == '.':
                match_key = match.course[:8]
                match_key = regex.sub(" ", match_key)
                matches[match_key].append(match)
            else:
                match_key = match.course[:9]
                match_key = regex.sub(" ", match_key)
                matches[match_key].append(match)
    return matches
