'''
library.py -- contains all library functions for virtualgrade, available to all
Created by: Adam Plumer
Date created: Nov 8, 2016
'''

from . import file_manager
from . import auth
from . import constants as cons
import cgi,sys,os
import logging

from importlib import import_module
import json


class BadArgsException(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)


'''
get_user -- gets the user's Linux login, grading groups, and admin groups
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
def get_user():
        remote_user = auth.get_user()
        admin, grading = auth._get_admin_grading()

        courses = auth._get_courses()

        return (remote_user, admin, grading, courses)


'''
check_args -- determines whether all args in a list are valid args (read: not None)
              raises BadArgsException if invalid args, otherwise returns
'''
def check_args(args):
        for arg,val in args.items():
                if val is None:
                        raise BadArgsException(arg + " is None")
        return


'''
get_adetails -- gets the assignment details for a given assignment in a given course
             e.g. ('00', 'hw4') -> {'type' : 'pdf', 'pages' : '6', ...}
'''
def get_adetails(course, assignment):
        page_list = file_manager.read_alist(course)
        return page_list[assignment] if assignment in page_list else {}


'''
get_type -- gets the assignment type for a given assignment in a given course
             e.g. ('00', 'hw4') -> 'pdf'
'''
def get_type(course, assignment):
        adetails = get_adetails(course, assignment)
        return adetails['type'] if adetails != {} else ''


'''
get_students_for_grading -- takes in the request form and parses out the course
                            and assignment, gets the type for the assignment,
                            then retrives the students from that type's module
'''
def get_students_for_grading(form):
        response = {}

        course = form.getvalue('course')
        assignment = form.getvalue('assign')

        check_args({'course': course, 'assignment': assignment})

        auth.check_is_grader(course)

        assign_type = get_type(course, assignment)

        try:
                os.chdir(cons.LIB_PATH)
                if assign_type in cons.VALID_MODULES:
                        module = import_module('.' + assign_type, 'virtualgrade')
                else:
                        logging.error('Tried to invoke invalid module:' + assign_type)
                        raise Exception('Tried to invoke invalid module:' + assign_type)
                response = module.get_students_for_grading(course, assignment)
                response['type'] = assign_type

        except Exception as e:
                response['error'] = str(e)

        return response


'''
get_assignments_for_grading -- gets a list of all assignments available for
                               grading for a particular course
'''
def get_assignments_for_grading(form):
        response = {}
        
        course = form.getvalue('course')
        check_args({'course': course})

        auth.check_is_grader(course)

        pages = file_manager.read_alist(course)

        response['courses'] = []

        for key in pages:
                response['courses'].append(key)

        return response


def get_grades_for_course(form):
        response = {}
        
        course = form.getvalue('course')
        check_args({'course':course})
        user = auth.get_user()

        score_file = file_manager.read_score(user, course)

        for key in score_file:
                response[key] = score_file[key]

        pages = file_manager.read_alist(course)
        
