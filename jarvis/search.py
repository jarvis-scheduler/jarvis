from jarvis.model import *
import pickle


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


def search(search):
    search = search.lower()

    with open('data/index.pickle', 'rb') as index_file:
        index = pickle.load(index_file)

    split = search.split()
    matches = []
    for x in range(len(split)):
        matches_raw = [v for (k, v) in index.items() if split[x] in k.lower()]
        if not x == 0:
            matches = [i for i in matches if i in matches_raw]
        else:
            matches = matches_raw
    return matches
