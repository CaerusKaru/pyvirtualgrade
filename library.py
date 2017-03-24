'''
library.py -- contains all library functions for virtualgrade, available to all
Created by: Adam Plumer
Date created: Nov 8, 2016
'''

from flask import Blueprint, session, request
from . import file_manager
from . import auth
from .course import Course
import json

library_page = Blueprint('library_page', __name__)

class BadArgsException(Exception):
        def __init__(self, value):
                self.value = value

        def __str__(self):
                return repr(self.value)

def _get_course():
        c = request.args.get('course')
        a = request.args.get('assign')
        se = request.args.get('semester')
        st = request.args.get('student') or session['username']
        p = request.args.get('problem')

        course = Course(c, se, a, st, p)

        return course

@library_page.route('/getUser', methods=['GET'])
def get_user():
        user, admin, grading, courses = _get_user()
        response = {}
        response['user'] = user
        response['archon'] = admin
        response['grading'] = grading
        response['courses'] = courses

        return json.dumps(response)

@library_page.route('/getType', methods=['GET'])
def get_type():
        course = _get_course()

        response = {}
        response['type'] = course.get_type()

        return json.dumps(response)

@library_page.route('/getGraders', methods=['GET'])
def get_graders():
        course = _get_course()
        
        response = {}
        response['graders'] = course.get_graders()

        return json.dumps(response)


@library_page.route('/getGrades', methods=['GET'])
def get_grades():
        course = _get_course()
        
        response = course.get_graders()
        response['type'] = course.get_type()

        return json.dumps(response)


@library_page.route('/getStudents', methods=['GET'])
def get_students():
        course = _get_course()

        response = course.get_students()
        response['type'] = course.get_type()

        return json.dumps(response)


def _get_all_pages(course_list, check_published):
        pages = []
        for course in course_list:
                alist = file_manager.read_alist(course)
                course_obj = {}
                course_obj['name'] = course
                if check_published:
                        assigns = [x for x in alist if alist[x]['publish']]
                else:
                        assigns = [x for x in alist]
                course_obj['assigns'] = assigns
                pages.append(course_obj)

        return pages


'''
_get_user -- gets the user's Linux login, grading groups, and admin groups
           args: none
           helper functions: _get_courses and _valid_course
           returns: four-tuple (remote_user, admin, grading, courses)
           notes:
                 - Here's the general thinking on the virtualgrade permissions
                   model:
                         - TAs: admin permissions, can do anything related to a
                                course, including grading
                         - Graders: can only grade, but can grade anyone in the
                                    course for any assignment
                         - Neither: students! they get a list of courses for
                                    which grades are available
'''


def _get_user():
        remote_user = auth.get_user()
        admin, grading = auth.get_admin_grading()
        courses = auth._get_courses()

        courses_full = _get_all_pages(courses, True)
        admin_full = _get_all_pages(admin, False)
        grading_full = _get_all_pages(grading, False)

        return (remote_user, admin_full, grading_full, courses_full)


'''
check_args -- determines whether all args in a list are valid args
              (read: not None)
              raises BadArgsException if invalid args, otherwise returns
'''


def check_args(args):
        for arg, val in args.items():
                if val is None:
                        raise BadArgsException(arg + " is None")
        return


'''
get_adetails -- gets the assignment details for a given assignment in a given
                course
             e.g. ('00', 'hw4') -> {'type' : 'pdf', 'pages' : '6', ...}
'''


def get_adetails(course, assignment):
        page_list = file_manager.read_alist(course)
        return page_list[assignment] if assignment in page_list else {}


'''
_get_type -- gets the assignment type for a given assignment in a given course
             e.g. ('00', 'hw4') -> 'pdf'
'''


def _get_type(course, assignment):
        adetails = get_adetails(course, assignment)
        return adetails['type'] if adetails != {} else ''
