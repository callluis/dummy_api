# -*- coding: utf-8 -*-
# Standard python libraries
import falcon
import uuid
import json
from contextlib import suppress

from api.common import BaseResource
from conf.config import LOG
from db.dummy import ACTIVE_USERS
from utils.errors import generic_error_handler
from utils.hashing_tools import make_password_hashing, checking_password_hash

class SignUp(BaseResource):
    """
    Handle for endpoint: /api/credentials
    """
    def __init__(self, **kwargs):
        """ Creates a client instance """
        super(SignUp, self).__init__(**kwargs)
        
    def on_post(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)

        if username in ACTIVE_USERS:
            error = {
                'description': 'Invalid username',
                'details': f'{username} already exists.'
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)

        tmp_user_info = {
            username: {
                'password': make_password_hashing(password),
                'api_key':  str(uuid.uuid4())
            }
        }

        ACTIVE_USERS.append(tmp_user_info)

        self.on_created(res, {f'{username}': 'has signed up'})

    def on_put(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)
        new_password = req.get_json('new_password', dtype=str, min=8, max=20)

        if not checking_password_hash(password, ACTIVE_USERS[username]['password']):
            error = {
                'description': 'Incorrect password entered',
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

        ACTIVE_USERS[username] = {
            'password': make_password_hashing(new_password),
            'api_key':  str(uuid.uuid4())
        }

        self.on_success(res, {'meta': f'password and apikey for {username} have been updated.'})

    def on_patch(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)
        new_password = req.get_json('new_password', dtype=str, min=8, max=20)

        if username not in ACTIVE_USERS:
            error = {
                'description': 'Invalid username',
                'details': f"{username} doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)
        
        if not checking_password_hash(password, ACTIVE_USERS[username]['password']):
            error = {
                'description': 'Incorrect password entered',
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

        ACTIVE_USERS[username]['password'] = make_password_hashing(new_password)

        self.on_success(res, {'meta': f'password has been updated for user {username}'})

    def on_delete(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)
        new_password = req.get_json('new_password', dtype=str, min=8, max=20)

        if username not in ACTIVE_USERS:
            error = {
                'description': 'Invalid username',
                'details': f"{username} doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)
        
        if not checking_password_hash(password, ACTIVE_USERS[username]['password']):
            error = {
                'description': 'Incorrect password entered',
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

        del ACTIVE_USERS[username]
        self.on_no_content(res, {})

# def on_post(self, req, res):
#         # ACTIVE_USERS = {
#         #     'tom': {
#         #         'password': 'whatever',
#         #         'secret':   'revetahw'
#         #     }
#         # }

#         username = req.get_json('username', dtype=str, min=3, max=20)
#         password = req.get_json('password', dtype=str, min=8, max=20)

#         if not username:
#             error = {
#                 'title': 'Invalid username',
#                 'description': f'{username} is not valid'
#             }
#             LOG.error(error)
#             raise generic_error_handler(400, req=req, error_override=error)

#         if username in ACTIVE_USERS:
#             error = {
#                 'title': 'Invalid username',
#                 'description': f'{username} already exists.'
#             }
#             LOG.error(error)
#             raise generic_error_handler(400, req=req, error_override=error)
       
#         # Create an api_key
#         api_key = str(uuid.uuid4())

#         tmp_user_info = {
#             username: {
#                 'password': make_password_hashing(password),
#                 'api_key':  api_key
#             }
#         }

#         ACTIVE_USERS.append(tmp_user_info)

#         self.on_created(res, {})



# def Login(self):
#     if checking_password_hash(password_python, hobbyist.password) == True:
#         session['hobbyist'] = hobbyist_python
#         flash('Welcome back, ' + str(hobbyist_python) + '.', 'allgood')
#         return redirect("/")
#     elif checking_password_hash(password_python, hobbyist.password) == False:
#         flash("Sorry " + str(hobbyist_python) + ", that was not your password. :( ", "error10")
#         #return redirect("/login")
#         return render_template('zlogin.html', hobbyistname=hobbyist_python)
            

# @falcon.before(validate_jwt_token)
