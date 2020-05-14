# -*- coding: utf-8 -*-
# Standard python libraries
import falcon
import uuid
import json
from contextlib import suppress

from api.common import BaseResource
from conf.config import LOG, SUPER_ADMIN_KEY
from db import database as db
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
        # import pdb
        # pdb.set_trace()
        if "multipart/form-data" in req.content_type:
            username = req.params.get('username') 
            password = req.params.get('password')
        elif "application/json" in req.content_type:
            username = req.get_json('username', dtype=str, min=3, max=20)
            password = req.get_json('password', dtype=str, min=8, max=20)
        else:
            error = {
                'description': 'Invalid content-type',
                'details': 'Only \'multipart/form-data\' and \'json/application\' allowed'
            }
            LOG.error(error)
            raise generic_error_handler(415, req=req, error_override=error)

        users = db.fetch_users(username)
        if len(users) >= 1:
            error = {
                'description': 'Invalid username',
                'details': f"user '{username}' already exists."
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)
        else:
            user_id = str(uuid.uuid4())
            pasword = make_password_hashing(password)

            db.create_user(user_id, username, pasword)

            data = {
                'id': user_id,
                'username': username
            }

            self.on_created(res, data)

    def on_put(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)
        new_password = req.get_json('new_password', dtype=str, min=8, max=20)

        users = db.fetch_users(username)

        user_id = str(uuid.uuid4())
        pasword = make_password_hashing(new_password)

        if len(users) == 1:
            if not checking_password_hash(password, users[0]['password']):
                error = {
                    'description': 'Incorrect password entered',
                }
                LOG.error(error)
                raise generic_error_handler(401, req=req, error_override=error)
            else:
                db.replace_user_info(user_id, username, pasword)
                
        elif len(users) > 1:
            error = {
                'description': f"There was more than 1 user found for username: '{username}'"
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)
        else:
            db.create_user(user_id, username, pasword)
        
        data = {
            'id': user_id,
            'username': username
        }

        self.on_success(res, data)

    def on_patch(self, req, res):
        username = req.get_json('username', dtype=str, min=3, max=20)
        password = req.get_json('password', dtype=str, min=8, max=20)
        new_password = req.get_json('new_password', dtype=str, min=8, max=20)

        pasword = make_password_hashing(new_password)
        
        users = db.fetch_users(username)

        if len(users) == 1:
            if not checking_password_hash(password, users[0]['password']):
                error = {
                    'description': 'Incorrect password entered',
                }
                LOG.error(error)
                raise generic_error_handler(401, req=req, error_override=error)
            else:
                db.update_password(users[0]['id'], pasword)
                data = {
                    'id': users[0]['id'],
                    'username': username
                }

                self.on_success(res, data)

        elif len(users) > 1:
            error = {
                'description': f"There was more than 1 user found for username: '{username}'"
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)

        else:
            error = {
                'description': 'Invalid username',
                'details': f"{username} doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)

    def on_delete(self, req, res, user_id=None):
        if user_id:
            user = db.fetch_users(None, user_id=user_id)

            if user:
                if req.get_header('SUPER_ADMIN_KEY') == SUPER_ADMIN_KEY:
                    db.delete_from_table(user_id)
                    self.on_no_content(res, {})
                else:
                    error = {
                        'description': 'Unauthorized',
                        'details': "Permission Denied" 
                    }
                    LOG.error(error)
                    raise generic_error_handler(401, req=req, error_override=error)
            else:
                error = {
                    'description': 'Invalid user_id',
                    'details': f"{user_id} doesn't exist."
                }
                LOG.error(error)
                raise generic_error_handler(404, req=req, error_override=error)

        else:
            raise generic_error_handler(500, req=req)

    def on_get(self, req, res):
        if req.get_header('SUPER_ADMIN_KEY') == SUPER_ADMIN_KEY:
            username = req.params.get('username')
            user_id = req.params.get('id')
            users = db.fetch_users(username=username, user_id=user_id, hide_pass=True)
            self.on_success(res, {'items': users})
        else:
            error = {
                'description': 'Unauthorized',
                'details': "Permission Denied" 
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)
        
        

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
