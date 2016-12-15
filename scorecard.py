'''
scorecard.py -- module for grading an assignment using an explicit scorecard
Created by: Adam Plumer
Date created: Nov 17, 2016

The idea for the scorecard is that there is always an explicit rubric to
base the score on:

*-------------*--------------*
|             |              |
|   Content   |    Rubric    |
|             |              |
|             |              |
|             |              |
|             |              |
|             |              |
*-------------*--------------*

The remaining design question for this module is: where do we store the
templates for the rubric? The current thinking is that we include it in
the grading directory, that way instructors can reuse existing templates
easily, without it getting lost in the archives of VirtualGrade. The other
thinking is that the VirtualGrade archive exists for this exact reason.

Either way, the generation for these templates will have to occur in the
setup page on VirtualGrade, simply because the actual template is stored
as a JSON object for later extraction/saving

'''

from . import file_manager
from . import constants
from . import auth


def get_students_for_grading(course, assignment):
        auth.check_is_grader(course)

        response = {}

        names = set(file_manager.get_students_for_assignment(course, assignment))

        com = file_manager.read_completed(course, assignment)
        inp = file_manager.read_inprogress(course, assignment)

        names = list(names.difference(set(com), set(inp)))
        
        response['com'] = com['names'] if 'names' in com else []
        response['inp'] = inp['names'] if 'names' in inp else []
        response['names'] = names

        return response
