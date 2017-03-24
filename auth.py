'''
auth.py -- contains the authentication model for virtualgrade, available to all
Created by: Adam Plumer
Date created: Dec 9, 2016
'''

import os
import ldap

from flask import Blueprint, session, request, escape
from . import constants as cons
from functools import wraps
from re import split
from subprocess import Popen, PIPE


auth_page = Blueprint('auth_page', __name__)
_LDAP_URL = 'ldap://ldap.eecs.tufts.edu'

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


@auth_page.route('/login', methods=['POST'])
def login():

        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
        else:
                username = request.args.get('username')
                password = request.args.get('password')
        user_ldap = 'uid='+username+',ou=People,dc=eecs,dc=tufts,dc=edu'
        admin = []
        grading = []

        try:
                con = ldap.initialize(_LDAP_URL)

                try:
                        con.simple_bind_s(user_ldap, password)
                        admin, grading = _get_admin_grading(username)
                except ldap.INVALID_CREDENTIALS:
                        raise NoAuthException('invalid username/password')
                except:
                        raise NoAuthException('password empty/LDAP error')
        except NoAuthException as e:
                raise e
        except ldap.LDAP_ERROR:
                pass
        finally:
                con.unbind()

        session['username'] = username
        session['admin'] = admin
        session['grading'] = grading

        return 'login success', 200

@auth_page.route('/logout', methods=['POST'])
def logout():
        session.pop('username', None)
        session.pop('admin', None)
        session.pop('grading', None)

        return 'logged out', 200


'''
_get_remote_user -- returns the Linux username of the current requester
                    * Currently retrieved as REMOTE_USER, authenticated by LDAP
'''


def _get_remote_user():

        if 'username' in session:
                user = session['username']
                admin = session['admin']
                grading = session['grading']

        else:
                raise NoUserException()

        return user, admin, grading


def get_user():
        user, admin, grading = _get_remote_user()
        return user


def get_admin_grading():
        user, admin, grading = _get_remote_user()
        return admin, grading


'''
_map_courses -- mapping function to return the course name without extension
                e.g. 00.hw4.* -> 00
'''


def _map_courses(s):
        return s.split(".")[0]


'''
_get_courses -- gets all courses in which grades are available for current
                request user
                e.g. 'aplume01' -> ['00', '15', '20']
'''


def _get_courses():
        user = get_user()
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
_get_admin_grading -- returns all TA and grading groups for current request
                      user
                      Order: admin, grading
                      E.g. aplume01 -> (['170', '00'], ['170', '00', '15'])
'''


def _get_admin_grading(remote_user):

        pipe_cmd = ['groups', remote_user]
        raw_data = Popen(pipe_cmd, stdout=PIPE).stdout.read().strip().decode()
        groups = raw_data.split(' ')[2:]

        admin = [x[2:] for x in groups
                 if x.startswith('ta') and x[2].isdigit()]
        grading = [x[5:] for x in groups
                   if x.startswith('grade') and x[5].isdigit()]

        grading += admin
        grading = list(set(grading))

        return admin, grading


def _get_graders(course):
        graders = []

        try:
                pipe_cmd = ['getent', 'group', course]
                raw_data = Popen(pipe_cmd, stdout=PIPE).stdout.read().strip()
                csv_graders = split(':', raw_data.decode())[3]
                graders = split(',', csv_graders)
                try:
                        graders.remove('vgrade')
                        graders.remove('provide')
                except:
                        pass
        except:
                pass

        return graders


def admin(f):
        @wraps(f)
        def dec_func(*args, **kwargs):
                if kwargs['course'] not in session['admin']:
                        raise NoAuthException()
                return f(*args, **kwargs)
        return dec_func


def grader(f):
        @wraps(f)
        def dec_func(*args, **kwargs):
                if kwargs['course'] not in session['grading']:
                        raise NoAuthException()
                return f(*args, **kwargs)
        return dec_func


'''
get_permissions -- gets whether current request user is an admin or a grader
                   for a given course
'''


def get_permissions(course):
        admin, grading = get_admin_grading()
        is_admin = course in admin
        is_grader = is_admin or course in grading
        return is_admin, is_grader
