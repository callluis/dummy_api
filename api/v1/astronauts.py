# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Standard python libraries
import falcon
import uuid
import json
from collections import OrderedDict
from contextlib import suppress

from api.common import BaseResource
from conf.config import LOG, SUPER_ADMIN_KEY
from db_ import database as db
from middleware.jwt_authentication import validate_token
from utils.errors import generic_error_handler
from utils.hashing_tools import make_password_hashing, checking_password_hash
from utils.jwt_module import jwt_payload_handler

class List(BaseResource):
    """
    Handle for endpoint: /api/credentials
    """
    def __init__(self, **kwargs):
        """ Creates a client instance """
        super(List, self).__init__(**kwargs)
    
    @falcon.before(validate_token)
    def on_get(self, req, res):
        params = req.params
        if params.get('id'):
            params['id_'] = params['id'] 
        astronauts = db.fetch_astronauts(filters=params)
        data = {'count': len(astronauts), 'items': astronauts}
        self.on_success(res, data)
    
    @falcon.before(validate_token)
    def on_post(self, req, res):
    
        skills = req.get_json('skills')

        if not isinstance(skills, list):
            error = {
                'description': 'invalid skills',
                'details': f"'skills' field needs to be an array/list"
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)

        astronaut = {
            'id': str(uuid.uuid4()),
            'active': True,
            'firstName': req.get_json('firstName', dtype=str, min=3, max=20),
            'lastName': req.get_json('lastName', dtype=str, min=3, max=20),
            'skills': skills,
            'hoursInSpace': req.get_json('hoursInSpace', dtype=int, min=0),
            'picture': req.get_json('picture', dtype=str, min=3)
        }
        
        try:
            db.add_astronauts_bulk([astronaut])
        except Exception as ex:
            error = {
                'description': str(ex)
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)

        self.on_created(res, astronaut)

class Detail(BaseResource):
    """
    Handle for endpoint: /api/credentials/
    """
    def __init__(self, **kwargs):
        """ Creates a client instance """
        super(Detail, self).__init__(**kwargs)

    @falcon.before(validate_token)
    def on_get(self, req, res, id_):
        params = {'id_': id_}
        astronauts = db.fetch_astronauts(filters=params)
        if astronauts:
            data = astronauts[0]
        else:
            error = {
                'description': 'Invalid astronaut',
                'details': f"An astronaut with id '{id_}' doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)
        self.on_success(res, data)

    @falcon.before(validate_token)
    def on_delete(self, req, res, id_):
        params = {'id_': id_}
        astronauts = db.fetch_astronauts(filters=params)
        if astronauts:
            data = astronauts[0]
            astronaut_id = astronauts[0]['id']
            db.delete_from_table('astronauts', astronaut_id)
            
        else:
            error = {
                'description': 'Invalid astronaut',
                'details': f"An astronaut with id '{id_}' doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)
        if req.params.get('details') == 'true':
            data['meta'] = {'action': f'astronaut {astronauts[0]["firstName"]} {astronauts[0]["lastName"]} has been deleted'}
            self.on_success(res, data)
        else:
            self.on_no_content(res, {})
        
    @falcon.before(validate_token)
    def on_patch(self, req, res, id_):
        params = {'id_': id_}
        astronauts = db.fetch_astronauts(filters=params)
        if astronauts:
            data = astronauts[0]
        
            payload = OrderedDict()
            payload["active"] = req.get_json("active", default=data['active'])
            payload["firstName"] = req.get_json("firstName", default=data['firstName'])
            payload["lastName"] = req.get_json("lastName", default=data['lastName'])
            skills = req.get_json("skills", default=data['skills'])
            if not isinstance(skills, list):
                error = {
                    'description': 'invalid skills',
                    'details': f"'skills' field needs to be an array/list"
                }
                LOG.error(error)
                raise generic_error_handler(400, req=req, error_override=error)
            payload["skills"] = skills
            payload["hoursInSpace"] = req.get_json("hoursInSpace", default=data['hoursInSpace'])
            payload["picture"] = req.get_json("picture", default=data['picture'])

            astronaut = db.update_astronaut_info(id_, fields=payload)

        else:
            error = {
                'description': 'Invalid astronaut',
                'details': f"An astronaut with id '{id_}' doesn't exist."
            }
            LOG.error(error)
            raise generic_error_handler(404, req=req, error_override=error)

        self.on_success(res, astronaut)
