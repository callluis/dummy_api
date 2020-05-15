# -*- coding: utf-8 -*-
# Standard python libraries
import falcon
import uuid
import json
from collections import OrderedDict
from contextlib import suppress

from api.common import BaseResource
from conf.config import LOG, SUPER_ADMIN_KEY
from db import database as db
from utils.errors import generic_error_handler
from utils.hashing_tools import make_password_hashing, checking_password_hash
from utils.jwt_module import jwt_payload_handler

class Users(BaseResource):
    """
    Handle for endpoint: /api/credentials
    """
    def __init__(self, **kwargs):
        """ Creates a client instance """
        super(Users, self).__init__(**kwargs)
        
    def on_post(self, req, res):
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
            users = db.fetch_users(None, user_id=user_id)

            if users:
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

    def on_get(self, req, res, user_id=None):
        if req.get_header('SUPER_ADMIN_KEY') == SUPER_ADMIN_KEY:
            if user_id:
                users = db.fetch_users(user_id=user_id, hide_pass=True)
                if users:
                    data = {
                        'id': user_id,
                        'username': users[0]['username']
                    }
                else:
                    error = {
                        'description': 'Invalid user_id',
                        'details': f"{user_id} doesn't exist."
                    }
                    LOG.error(error)
                    raise generic_error_handler(404, req=req, error_override=error)
            else:
                username = req.params.get('username')
                user_id = req.params.get('id')
                users = db.fetch_users(username=username, user_id=user_id, hide_pass=True)
                data = {'items': users}
            self.on_success(res, data)
        else:
            error = {
                'description': 'Unauthorized',
                'details': "Permission Denied" 
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

class JWTLogin(BaseResource):
    """
    Handle for endpoint: /api/credentials/
    """
    def __init__(self, **kwargs):
        """ Creates a client instance """
        super(JWTLogin, self).__init__(**kwargs)

    def on_post(self, req, res):
        username = req.get_json('username', dtype=str)
        password = req.get_json('password', dtype=str)

        users = db.fetch_users(username)
        if len(users) == 1:
            if not checking_password_hash(password, users[0]['password']):
                error = {
                    'description': 'either username or password is invalid'
                }
                LOG.error(error)
                raise generic_error_handler(401, req=req, error_override=error)
            else:
                payload = OrderedDict()
                payload['id'] = users[0]['id']
                payload['username'] = username
                
                data = jwt_payload_handler(payload)

                payload = {**payload, **data}

                self.on_success(res, payload)

        
        elif len(users) > 1:
            error = {
                'description': f"There was more than 1 user found for username: '{username}'"
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

        else:
            error = {
                'description': 'either username or password is invalid'
            }
            LOG.error(error)
            raise generic_error_handler(401, req=req, error_override=error)

# @falcon.before(validate_jwt_token)
