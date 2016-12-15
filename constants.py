'''
constants.py -- contains all necessary library constants, mostly for file
                management
Created by: Adam Plumer
Date created: Nov 8, 2016
'''

import os, pwd, getpass  # to get home directory

# MOVE TO ENV ASAP
SECRET_KEY = '64q,Jvgj~B73?1-6&$.^fiD3zT0];8jB2of%V9^dl.WG1|G1X5j6eEPRe5y7|K>'


def _storage_owner(path):
    owner = pwd.getpwuid(os.stat(path).st_uid)[0]
    return owner == getpass.getuser()

'''
FILE PATHS:
- root: file path for the virtual host
- grades: file path for grades repository
- comp: root directory for all courses
- grading: provide directory path
- assign: VirtualGrade assignment directory
- alist: parameters file
- completed: list of completed students for
             an assignment
- inprogress: list of currently-grading students
              for an assignment
- lib: path to this module, in case subprocess
       needs to run local scripts (e.g. groups)
'''
ROOT_PATH = os.path.expanduser('~') + '/'
STORAGE_PATH = '/r/virtualgrade/' if _storage_owner('/r/virtualgrade/grades/') else ROOT_PATH
GRADES_PATH = STORAGE_PATH + 'grades/'
COMP_PATH = '/comp/'
GRADING_PATH = '/grading/'
ASSIGN_PATH = STORAGE_PATH + 'assignments/'
ALIST_PATH = '/alist'
LIB_PATH = ROOT_PATH + 'vgrade/'
COMPLETED_FILE = 'completed'
INPROGRESS_FILE = 'inprogress'
PROVIDE_SRC = 'provide'

'''
VALID MODULES:
- pdf
- scorecard
'''
VALID_MODULES = ['pdf', 'scorecard']

'''
get_course_grading_path -- returns the absolute path for a course's grading dir
'''
def get_course_grading_path(course):
        return COMP_PATH + course + GRADING_PATH


'''
MESSAGES:
- error-module: cannot find module at switchboard
- no-module: cannot find a module for a given type
'''
ERROR_MODULE_MSG = "cannot find method"
NO_MODULE_FOUND_MSG = "unknown method/type"

