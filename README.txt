----------------------------------------------*
|                                              |
|             Virtual Grade 2.0                |
|       A Linux-based, Python library          |
|       course grading solution                |
|                                              |
*----------------------------------------------*

Created by: Adam Plumer
Based on original implementation by C. Gregg
Date created: Fall-Winter 2016

The idea behind Virtual Grade is simple: to
provide a modular, interactive platform to
grade student submissions through a web-based 
system

This system comes in two pieces:
(1) Python backend to handle file management
(2) AngularJS frontend to handle user interaction

The description for (1) is in the README in
the public_html directory

Here's the basic premise for PyVirtualGrade:

*-------------*     *---------*
|  read-only  | (1) | grading | (2)
| submissions | --> | website |
*-------------*     *---------*

                /
               / (3)
              *
  *--------*
  | graded |
  |  repo  |
  *--------*


This library is responsible for (1) and (3) above,
handling requests from the grading website as
needed. This means that for every aspect of the
website, there is a counterpart API enabled on
the backend. For instance, get_grades_for_course
would return the list of grades for a given
course, divided by assignment, for a given user,
and save_graded_submission would save a marked
up submission in the graded repo

One of the hallmarks of this system is its
adaptability to various grading forms. For any
given grading type, there is a library of
file-handling, permissions-checking and 
pre-planned formats to enable module creators
to easily and effectively add to this system

*----------------Changelog-------------------*

12-15-16:

- Added authentication model using LDAP and
  Javascript Web Tokens (JWT)

11-25-16:

- Initialized Git repo
- Added exceptions for no user to library


11-17-16:

- Initialized the scorecard module, brushed
  up existing files and fixed the formatting,
  and created the grading retrieval model
- Added inprogress read function to file
  manager


11-16-16:

- Fixed the pdf module and library interface
  for retrieving initial grading data


11-14-16:

- Fixed permissions methods to check for
  permissions independent of passed
  parameters (safer than previous)
- Added exception handling for os.listdir
- Added comments for existing methods


11-10-16:

- Created file_manager module to allow for
  safe file I/O
- Initialized pdf and scorecard modules,
  preparing to copy over a lot of existing
  framework


11-09-16:

- Added methods for accessing student
  information for particular courses and
  assignments


11-08-16:

- Initialized library, created constants file
- Brought over current scripts from 2.0beta
- Added get_user method to retrieve groups
  for a given user


