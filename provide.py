'''
provide.py -- wrapper for A. Couch Provide system
Created by: Adam Plumer
Date created: Dec 6, 2016
'''


import os
from . import constants
from . import auth


def _check_folder(path, folder):
        folders = []
        try:
                folders = os.listdir(path)
        except OSError as e:
                pass
        except:
                pass

        return folder in folders


def _high_sub(s):
        return s.split('.')[1]


def _get_latest(path, student):
        all_subs = os.listdir(path)
        student_subs = [x for x in all_subs if x.split('.')[0] == student]

        return max(student_subs, key=_high_sub)


'''
get_problem -- read the file source in the provide directory
'''

@auth.grader
def get_problem(course='', assignment='', student='', src=''):

        full_path = constants.COMP_PATH

        if not _check_folder(full_path, course):
                return ''

        full_path += course + constants.GRADING_PATH

        if not _check_folder(full_path, assignment):
                return ''

        full_path += assignment

        latest_sub = _get_latest(full_path, student)
        if latest_sub == '':
                return ''

        full_path += "/" + latest_sub + "/"

        if not _check_folder(full_path, src):
                return ''

        full_path += src

        try:
                with open(full_path, 'r') as f:
                        return ''.join(f.read().splitlines())
        except:
                return ''


'''
get_students_for_assignment -- gets a list of all students in a provide
                               directory for a particular course and
                               assignment
'''

@auth.grader
def get_students_for_assignment(course='', assignment=''):

        full_path = constants.COMP_PATH

        if not _check_folder(full_path, course):
                return []

        full_path += course + constants.GRADING_PATH

        if not _check_folder(full_path, assignment):
                return []

        full_path += assignment

        names = []
        try:
                names = [name.split('.')[0] for name in os.listdir(full_path)
                         if os.path.isdir(os.path.join(full_path, name))]
        except OSError as e:
                pass
        except:
                pass

        return list(set(names))
