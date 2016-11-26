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

import constants, file_manager, library


def _get_names_by_page(course, assignment, page):

        names = library.get_students_for_assignment(course, assignment)

        num_names = len(names)
        num_names = num_names if num_names != 0 else 1

        '''
        COMPLETED FILE:
                stores as:
                { '1' : ['aplume01','molay'], '2' : ['cgregg','hescott'], ... }
        '''

        com = file_manager.read_completed(course, assignment)
        num_com = len(com[page]) if com != [] else 0
        
        return num_names, num_com


def get_students_for_grading(course, assignment):
        pages = []
        num_pages = int(library.get_adetails(course, assignment)['pages'])

        response = {}

        for i in range(0, num_pages):
                page = {}
                page['num'] = (i+1) # done this way to prevent zero-indexing
                num_names, num_com = _get_names_by_page(course, assignment, str(i+1))
                num_done = (float(num_com)/num_names)*100
                page['progress'] = num_done
                pages.append(page)

        response['pages'] = pages
        return response

