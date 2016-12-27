'''
auth.py -- contains the authentication model for virtualgrade, available to all
Created by: Adam Plumer
Date created: Dec 9, 2016
'''

import os
from http import cookies
import jwt
from datetime import datetime, timedelta
import ldap
from urllib import parse

from . import constants as cons
from re import split
from subprocess import Popen, PIPE


_REFRESH_TIME = timedelta(hours=1)
_AUTH_TIME = timedelta(days=3)
_AUTH_TOKEN = ''


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


def _check_auth_token(auth_token, refresh_token):

        try:
                # switch to -> os.environ['SECRET_KEY'])
                jwt.decode(auth_token, cons.SECRET_KEY)
        except jwt.ExpiredSignatureError:
                return _check_refresh_token(refresh_token)
        except:
                raise NoUserException('cannot decode token')
        else:
                return auth_token


def _check_refresh_token(refresh_token):

        payload = {}
        try:
                # switch to -> os.environ['SECRET_KEY'])
                payload = jwt.decode(refresh_token, cons.SECRET_KEY)
        except jwt.ExpiredSignatureError:
                raise NoUserException('refresh token expired')
        except:
                raise NoUserException('cannot decode token')
        else:
                admin, grading = _get_admin_grading(payload['username'])
                auth_payload = {
                        'username': payload['username'],
                        'admin': admin,
                        'grading': grading,
                        'exp': datetime.utcnow() + _AUTH_TIME
                }
                # switch to -> os.environ['SECRET_KEY']
                return jwt.encode(auth_payload, cons.SECRET_KEY,
                                  algorithm='HS256')


def get_empty_tokens():
        auth_cookie = cookies.Morsel()
        auth_cookie['httponly'] = True
        auth_cookie['secure'] = True
        auth_cookie.set('vg-auth', '', parse.quote(''))
        ref_cookie = cookies.Morsel()
        ref_cookie['httponly'] = True
        ref_cookie['secure'] = True
        ref_cookie.set('vg-ref', '', parse.quote(''))

        return auth_cookie, ref_cookie


def login(username, password):
        username = username if username is not None else ''
        password = password if password is not None else ''
        user_ldap = 'uid='+username+',ou=People,dc=eecs,dc=tufts,dc=edu'
        auth_cookie, ref_cookie = get_empty_tokens()

        try:
                con = ldap.initialize('ldaps://ldap.eecs.tufts.edu:636')

                try:
                        con.simple_bind_s(user_ldap, password)
                        # switch to -> 'SECRET_KEY' not in os.environ:
                        if cons.SECRET_KEY == '':
                                return auth_cookie, ref_cookie, False
                        # switch to -> os.environ['SECRET_KEY']
                        secret_key = cons.SECRET_KEY

                        admin, grading = _get_admin_grading(username)

                        auth_payload = {
                                'username': username,
                                'admin': admin,
                                'grading': grading,
                                'exp': datetime.utcnow() + _AUTH_TIME
                        }

                        refresh_payload = {
                                'username': username,
                                'exp': datetime.utcnow() + _REFRESH_TIME
                        }

                        auth_token = jwt.encode(auth_payload, secret_key,
                                                algorithm='HS256')
                        refresh_token = jwt.encode(refresh_payload, secret_key,
                                                   algorithm='HS256')

                        auth_cookie.set('vg-auth', auth_token,
                                        parse.quote(auth_token))
                        ref_cookie.set('vg-ref', refresh_token,
                                       parse.quote(refresh_token))

                except ldap.INVALID_CREDENTIALS:
                        # raise NoAuthException('invalid username/password')
                        return auth_cookie, ref_cookie, False
                except:
                        # raise NoAuthException('password empty/LDAP error')
                        return auth_cookie, ref_cookie, False
        except:
                return auth_cookie, ref_cookie, False

        finally:
                con.unbind()

        return auth_cookie, ref_cookie, True


'''
_get_remote_user -- returns the Linux username of the current requester
                    * Currently retrieved as REMOTE_USER, authenticated by LDAP
'''


def _get_remote_user():

        if 'HTTP_COOKIE' in os.environ:
                cookie_string = os.environ.get('HTTP_COOKIE')
                c = cookies.SimpleCookie()
                c.load(cookie_string)

                try:
                        auth_token = c['vg-auth'].value
                        ref_token = c['vg-ref'].value

                        auth_token = _check_auth_token(auth_token, ref_token)
                        c['vg-auth'] = auth_token
                        # switch to -> os.environ['SECRET_KEY'])
                        payload = jwt.decode(auth_token, cons.SECRET_KEY)
                        user = payload['username']
                        admin = payload['admin']
                        grading = payload['grading']
                        _AUTH_TOKEN = auth_token
                        return user, admin, grading

                except KeyError:
                        raise NoUserException('unable to get token values')
        else:
                raise NoUserException('unable to retrieve cookies')


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

'''
check_is_grader -- determines whether current request user is a grader for a
                   given course
                   * raises NoAuthException if not grader
'''


def check_is_grader(course):
        admin, grading = get_admin_grading()
        test = course in grading
        if not test:
                raise NoAuthException("not a grader for " + course)

        return


'''
check_is_admin -- determines whether current request user is an admin for a
                  given course
                  * raises NoAuthException if not admin
'''


def check_is_admin(course):
        admin, grading = get_admin_grading()
        test = course in admin
        if not test:
                raise NoAuthException("not an admin for " + course)

        return


'''
get_permissions -- gets whether current request user is an admin or a grader
                   for a given course
'''


def get_permissions(course):
        admin, grading = get_admin_grading()
        is_admin = course in admin
        is_grader = is_admin or course in grading
        return is_admin, is_grader
