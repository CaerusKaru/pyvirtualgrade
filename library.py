'''
library.py -- contains all library functions for virtualgrade, available to all
Created by: Adam Plumer
Date created: Nov 8, 2016
'''

import file_manager
import constants as cons
import library
import cgi,sys,os
import logging

from importlib import import_module
import json
from re import findall
from subprocess import Popen, PIPE

class NoUserException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class NoAuthException(Exception):
        def __init__(self, value):
                self.value = value
        def __str__(self):
                return repr(self.value)


'''
_get_remote_user -- returns the Linux username of the current requester
                    * Currently retrieved as REMOTE_USER, authenticated by LDAP
'''
def _get_remote_user():
	if 'REMOTE_USER' in os.environ:
		return os.environ['REMOTE_USER']
	else:
		raise NoUserException('no user available')

'''
_map_courses -- mapping function to return the course name without extension
                e.g. 00.hw4.* -> 00
'''
def _map_courses(s):
        return s.split(".")[0]


'''
_valid_course -- mapping function to return groups that are only valid
                 e.g. tape is not a TA group, but ta150 is
                 Hueristics: ta{} must be followed by at least one integer, as must grade{}
'''
def _valid_course(s):
        try: 
                int(s[0]) # we only care about the first digit after 'ta', e.g. 'ta1nlp' is acceptable
                return True
        except ValueError:
                return False

'''
_get_courses -- gets all courses in which grades are available for current request user
                e.g. 'aplume01' -> ['00', '15', '20']
'''
def _get_courses():
        user = _get_remote_user()
        course_path = cons.GRADES_PATH + user + "/"
        entries = []
        try:
                entries = os.listdir(course_path)
        except OSError as e:
                # log("problem with listdir")
                pass
        except:
                # log("some other problem")
                pass
        courses = list(set(map(_map_courses, entries)))
        return courses


'''
_get_admin_grading -- returns all TA and grading groups for current request user
                      Order: admin, grading
                      E.g. aplume01 -> (['170', '00'], ['170', '00', '15'])
'''
def _get_admin_grading():
        remote_user = _get_remote_user()
        os.chdir(cons.LIB_PATH)
        groups = Popen(['./gfind.sh', remote_user], stdout=PIPE).stdout.read().strip()
        
        groups += "," # added to allow indexing to end

        admin = findall("ta(.+?),", groups)
        admin = [s for s in admin if _valid_course(s)]

        grading = findall("grade(.+?),", groups)
        grading += admin
        grading = list(set(grading))

        return admin, grading


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
        remote_user = _get_remote_user()
        admin, grading = _get_admin_grading()

        courses = _get_courses()

        return (remote_user, admin, grading, courses)


'''
check_is_grader -- determines whether current request user is a grader for a given course
                   * raises NoAuthException if not grader
'''
def check_is_grader(course):
        admin, grading = _get_admin_grading()
        test = course in grading
        if not test:
                raise NoAuthException("not a grader for " + course)

        return


'''
check_is_admin -- determines whether current request user is an admin for a given course
                  * raises NoAuthException if not admin
'''
def check_is_admin(course):
        admin, grading = _get_admin_grading()
        test = course in admin
        if not test:
                raise NoAuthException("not an admin for " + course)

        return


'''
get_permissions -- gets whether current request user is an admin or a grader 
                   for a given course
'''
def get_permissions(course):
        admin, grading = _get_admin_grading()
        isAdmin = course in admin
        isGrader = isAdmin or course in grading
        return isAdmin, isGrader


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

        check_is_grader(course)
                      
        assign_type = get_type(course, assignment)
        
        try:
                os.chdir(cons.LIB_PATH)
                if assign_type in cons.VALID_MODULES:
                        module = import_module('.' + assign_type, 'virtualgrade')
                else:
                        logging.error('Tried to invoke invalid module:' + assign_type)
                        raise Exception
                response = module.get_students_for_grading(course, assignment)
                response['type'] = assign_type

        except Exception as e:
                response['error'] = cons.NO_MODULE_FOUND_MSG

        return response


'''
get_assignments_for_grading -- gets a list of all assignments available for
                               grading for a particular course
'''
def get_assignments_for_grading(form):
        response = {}
        
        course = form.getvalue('course')

        check_is_grader(course)

        pages = file_manager.read_alist(course)

        response['courses'] = []

        for key in pages:
                response['courses'].append(key)

        return response


def get_grades_for_course(form):
        response = {}
        
        course = form.getvalue('course')
        user = _get_remote_user()

        score_file = file_manager.read_score(user, course)

        for key in score_file:
                response[key] = score_file[key]

        pages = file_manager.read_alist(course)
        


'''
get_students_for_assignment -- gets a list of all students in a provide
                               directory for a particular course and
                               assignment
'''
def get_students_for_assignment(course, assignment):
        full_path = cons.COMP_PATH
        courses = []

        try:
                courses = os.listdir(full_path)
        except OSError as e:
                pass
        except:
                pass

        if course not in courses:
                return []

        full_path += course + cons.GRADING_PATH
        assignments = []

        try:
                assignments = os.listdir(full_path)
        except OSError as e:
                pass
        except:
                pass

        if assignment not in assignments:
                return []

        full_path += assignment
        names = []
        try:
                names = [name.split('.')[0] for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]
        except OSError as e:
                pass
        except:
                pass

        return names
        
