'''
pdf.py -- module for PDF markup grading system
Created by: Adam Plumer
Date created: Nov 12, 2016

Description:
PDF markup is nothing new. Just look at Preview on macOS, or any number of
sketch apps. The idea for this module is to move this functionality onto
the web, and allow markup of submitted documents, along with scoring.

The input for this module is a series of PDF documents in a surprising
number of combinations based on configuration. Some of these configurations
include:
- one problem per page
- multiple problems per page
- multiple pages per problem
- ...

The solution to this paradigm is to store everything relative to an individual
'problem'. E.g. p1 -> [p1.pdf, p2.pdf] or p1 -> [p1.pdf], which allows for
p1 -> A and p2 -> A for same-document access. NOTE: this means that it's up to
administrators to determine this format, and for students to conform to it. The
back-end mess to fix this is, at this moment, a nightmare. Added functionality
to resolve this is in the works...
'''

from . import constants
from . import file_manager
from . import library
from . import auth
from flask import Blueprint, session, request, make_response
import json

pdf_page = Blueprint('pdf_page', __name__)


def _get_names_by_page(course, assignment, page, com):

        names = file_manager.get_students_for_assignment(course=course, assignment=assignment)

        num_names = len(names)
        num_names = num_names if num_names != 0 else 1

        '''
        COMPLETED FILE:
                stores as:
                { '1' : ['aplume01','molay'], '2' : ['cgregg','hescott'], ... }
        '''

        num_com = len(com) if com != [] else 0

        return names, num_names, num_com


def get_grades(user, course, assignment):
        response = {}
        score_file = file_manager.read_score(user, course, assignment)
        response['grades'] = score_file
        details = library.get_adetails(course, assignment)
        response['published'] = details['publish_com']

        return response


def get_students_for_grading(course, assignment):
        pages = []
        num_pages = int(library.get_adetails(course, assignment)['pages'])

        response = {}
        com = file_manager.read_completed(course=course, assignment=assignment)

        for i in range(0, num_pages):
                page = {}
                page['num'] = (i+1)  # done this way to prevent zero-indexing
                names, num_names, num_com = _get_names_by_page(course,
                                                               assignment,
                                                               str(i+1),
                                                               com[str(i+1)])
                num_done = (float(num_com)/num_names)*100
                page['progress'] = num_done
                page['names'] = names
                page['com'] = com[str(i+1)]
                pages.append(page)

        response['pages'] = pages
        return response


def _find_next_student(course, assignment, problem):
        names = file_manager.get_students_for_assignment(course=course, assignment=assignment)
        com = file_manager.read_completed(course=course, assignment=assignment)

        unfinished_names = sorted([x for x in names if x not in com[problem]])

        if len(unfinished_names) > 0:
                return unfinished_names[0]
        else:
                return ''


@pdf_page.route('/getProblemForStudent', methods=['GET'])
def get_problem_for_student():
        response = {}

        course = request.args.get('course')
        assignment = request.args.get('assign')
        student = request.args.get('student')
        problem = request.args.get('problem')

        library.check_args({'course': course, 'assignment': assignment,
                            'problem': problem})

        src_convention = 'p' + problem + '.svg'

        @auth.grader
        def get_prob(course=''):
                svg = file_manager.get_problem(course=course, assignment=assignment, student=student,
                                               src=src_convention)

                response['svg'] = [svg]

                resp = make_response(json.dumps(response))
                resp.mimetype = 'text/plain'

                return resp

        return get_prob(course=course)


@pdf_page.route('/getNextStudent', methods=['GET'])
def get_next_student():
        course = request.args.get('course')
        assignment = request.args.get('assign')
        problem = request.args.get('problem')

        response = {}

        library.check_args({'course': course, 'assignment': assignment,
                            'problem': problem})

        next_student = _find_next_student(course, assignment, problem)

        if next_student == '':
                response['error'] = 'unable to find next student'
                return response

        score = file_manager.get_score_for_problem(course, assignment,
                                                   next_student, problem)

        response['student'] = next_student
        response['score'] = score

        return json.dumps(response)
