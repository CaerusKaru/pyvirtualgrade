'''
course.py -- a way to perform operations on a course consistently
Created by: Adam Plumer
Date created: Dec 27, 2016
'''

import os
from . import library
from . import constants as cons
from . import auth
from . import file_manager
from importlib import import_module


class Course:
        def __init__(self, course, semester=None, assign=None, student=None,
                     problem=None):
                if semester is None:
                        semester = cons.CUR_SEMESTER
                self.semester = semester
                self.course = course
                self.assign = assign
                self.student = student
                self.atype = None
                self.mod = None
                
                self._init_data()

        def _init_data(self):
                if self.assign is not None:
                        self.atype = library._get_type(self.course, self.assign)
                        try:
                                os.chdir(cons.LIB_PATH)
                                if self.atype in cons.VALID_MODULES:
                                        mod = '.' + self.atype
                                        self.mod = import_module(mod, 
                                                                 'virtualgrade')

                        except:
                                pass


        def get_graders(self):
                ta_graders = auth._get_graders('ta'+self.course)
                grade_graders = auth._get_graders('grade'+self.course)
                combined = ta_graders + grade_graders
                return list(set(combined))

        def get_assignments(self):
                pages = file_manager.read_alist(self.course)
                return [x for x in pages]

        def get_grades(self):
                if self.mod is None or self.assign is None:
                        return {}

                return self.mod.get_grades(self.student, self.course, 
                                           self.assign)

        def get_students(self):
                if self.mod is None or self.assign is None:
                        return {}

                return self.mod.get_students_for_grading(self.course, 
                                                         self.assign)

        def get_adetails(self):
                if self.assign is None:
                        return {}
                pages = file_manager.read_alist(self.course)
                return pages[self.assign] if self.assign in pages else {}

        def get_type(self):
                return self.atype

        def get_course(self):
                return self.course

        def get_assign(self):
                return self.assign

        def get_student(self):
                return self.student

        def get_problem(self):
                return self.problem
