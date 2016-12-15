'''
file_manager.py -- file manager for the Virtual Grade system
Created by: Adam Plumer
Date created: Nov 12, 2016
Notes:
   - This is the ONLY file that is authorized to do
     file I/O
   - All files in the Virtual Grade are in JSON format
   - This file responsibly handles any exceptions
     and permissions checking
   - All modules should have a detailed description
     of which files should contain certain information
     and be able to plan accordingly
   - Any feature requests should go to the current
     project manager for Virtual Grade
'''


import os, json
from . import auth
from . import constants
from . import provide


'''
_check_course -- makes sure that a course is available for reading/writing
'''
def _check_course(course):
        courses = []
        try:
                courses = os.listdir(constants.ASSIGN_PATH)
        except OSError as e:
                pass
        except:
                pass
        return course in courses


'''
_read_file -- PRIVATE function to read the contents of a file, returns
              empty list if any problems are encountered 
'''
def _read_file(filename):
        try:
                with open(filename, 'r') as f:
                        obj = {}
                        try:
                                obj = json.loads(f.read())
                        except:
                                pass
                        return obj
        except:
                return []


'''
read_alist -- gets the parameters file for a particular course
              - parameters file contains list of all assignments, types, and
                any extraneous information a module decides to store
'''
def read_alist(course):
        auth.check_is_grader(course)
        
        if not _check_course(course):
                return []
        else:
                full_path = constants.ASSIGN_PATH + course + constants.ALIST_PATH
                return _read_file(full_path)


'''
_get_source -- gets the file repository for an assignment in a specific course
'''
def _get_source(course, assignment):
        auth.check_is_grader(course)
        
        alist = read_alist(course)
        if (not alist == []) and (assignment in alist):
                adetails = alist[assignment]
                return adetails['source']
        return ''


'''
get_students_for_grading -- gets the list of students from the correct storage
                            repository
'''
def get_students_for_assignment(course, assignment):
        if _get_source(course, assignment) == constants.PROVIDE_SRC:
                return provide.get_students_for_assignment(course, assignment)
        return [] 


'''
get_problem -- reads in course, assignment, and student, along with the source file
               then retrieves the file source and returns it as raw data
'''
def get_problem(course, assignment, student, src):
        auth.check_is_grader(course)

        if _get_source(course, assignment) == constants.PROVIDE_SRC:
                return provide.get_problem(course, assignment, student, src)
        return ''


'''
read_completed -- reads in the file containing all info about 'completed' students
                  What does this mean?
                  - It's up to every module to come up with how to define 'completed',
                    and what information to store along with it
                  - This module's obligations are safe storage and retrieval of this
                    information, everything else is up to the responsible module
'''
def read_completed(course, assignment):
        auth.check_is_grader(course)
        
        if not _check_course(course):
                return []
        else:
                completed_path = constants.ASSIGN_PATH + course + "/"
                assigns = []
                try:
                        assigns = os.listdir(completed_path)
                except OSError as e:
                        pass
                except:
                        pass
                if assignment not in assigns:
                        return []
                else:
                        completed_path += assignment
                        files = []
                        try:
                                files = os.listdir(completed_path)
                        except OSError as e:
                                pass
                        except:
                                pass

                        if constants.COMPLETED_FILE in files:
                                completed_path += "/" + constants.COMPLETED_FILE
                                return _read_file(completed_path)
                        else:
                                return {}


'''
read_inprogress -- reads in the file containing all info about inprogress' students
                   What does this mean?
                   - It's up to every module to come up with how to define 'inprogress',
                     and what information to store along with it
                   - This module's obligations are safe storage and retrieval of this
                     information, everything else is up to the responsible module
'''
def read_inprogress(course, assignment):
        auth.check_is_grader(course)
        
        if not _check_course(course):
                return []
        else:
                completed_path = constants.ASSIGN_PATH + course + "/"
                assigns = []
                try:
                        assigns = os.listdir(completed_path)
                except OSError as e:
                        pass
                except:
                        pass
                if assignment not in assigns:
                        return []
                else:
                        completed_path += assignment
                        files = []
                        try:
                                files = os.listdir(completed_path)
                        except OSError as e:
                                pass
                        except:
                                pass

                        if constants.INPROGRESS_FILE in files:
                                completed_path += "/" + constants.INPROGRESS_FILE
                                return _read_file(completed_path)
                        else:
                                return {}

