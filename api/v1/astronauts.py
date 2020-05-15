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
from db import database as db
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
                'description': ex
            }
            LOG.error(error)
            raise generic_error_handler(400, req=req, error_override=error)

        self.on_created(res, astronaut)

    # def on_put(self, req, res):
    #     username = req.get_json('username', dtype=str, min=3, max=20)
    #     password = req.get_json('password', dtype=str, min=8, max=20)
    #     new_password = req.get_json('new_password', dtype=str, min=8, max=20)

    #     users = db.fetch_users(username)

    #     user_id = str(uuid.uuid4())
    #     pasword = make_password_hashing(new_password)

    #     if len(users) == 1:
    #         if not checking_password_hash(password, users[0]['password']):
    #             error = {
    #                 'description': 'Incorrect password entered',
    #             }
    #             LOG.error(error)
    #             raise generic_error_handler(401, req=req, error_override=error)
    #         else:
    #             db.replace_user_info(user_id, username, pasword)
                
    #     elif len(users) > 1:
    #         error = {
    #             'description': f"There was more than 1 user found for username: '{username}'"
    #         }
    #         LOG.error(error)
    #         raise generic_error_handler(400, req=req, error_override=error)
    #     else:
    #         db.create_user(user_id, username, pasword)
        
    #     data = {
    #         'id': user_id,
    #         'username': username
    #     }

    #     self.on_success(res, data)

    

    

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
        

    # def on_patch(self, req, res):
    #     username = req.get_json('username', dtype=str, min=3, max=20)
    #     password = req.get_json('password', dtype=str, min=8, max=20)
    #     new_password = req.get_json('new_password', dtype=str, min=8, max=20)

    #     pasword = make_password_hashing(new_password)
        
    #     users = db.fetch_users(username)

    #     if len(users) == 1:
    #         if not checking_password_hash(password, users[0]['password']):
    #             error = {
    #                 'description': 'Incorrect password entered',
    #             }
    #             LOG.error(error)
    #             raise generic_error_handler(401, req=req, error_override=error)
    #         else:
    #             db.update_password(users[0]['id'], pasword)
    #             data = {
    #                 'id': users[0]['id'],
    #                 'username': username
    #             }

    #             self.on_success(res, data)

    #     elif len(users) > 1:
    #         error = {
    #             'description': f"There was more than 1 user found for username: '{username}'"
    #         }
    #         LOG.error(error)
    #         raise generic_error_handler(400, req=req, error_override=error)

    #     else:
    #         error = {
    #             'description': 'Invalid username',
    #             'details': f"{username} doesn't exist."
    #         }
    #         LOG.error(error)
    #         raise generic_error_handler(404, req=req, error_override=error)

    # def on_delete(self, req, res, user_id=None):
    #     if user_id:
    #         users = db.fetch_users(None, user_id=user_id)

    #         if users:
    #             if req.get_header('SUPER_ADMIN_KEY') == SUPER_ADMIN_KEY:
    #                 db.delete_from_table(user_id)
    #                 self.on_no_content(res, {})
    #             else:
    #                 error = {
    #                     'description': 'Unauthorized',
    #                     'details': "Permission Denied" 
    #                 }
    #                 LOG.error(error)
    #                 raise generic_error_handler(401, req=req, error_override=error)
    #         else:
    #             error = {
    #                 'description': 'Invalid user_id',
    #                 'details': f"{user_id} doesn't exist."
    #             }
    #             LOG.error(error)
    #             raise generic_error_handler(404, req=req, error_override=error)

    #     else:
    #         raise generic_error_handler(500, req=req)


    # def on_post(self, req, res):
    #     username = req.get_json('username', dtype=str)
    #     password = req.get_json('password', dtype=str)

    #     users = db.fetch_users(username)
    #     if len(users) == 1:
    #         if not checking_password_hash(password, users[0]['password']):
    #             error = {
    #                 'description': 'either username or password is invalid'
    #             }
    #             LOG.error(error)
    #             raise generic_error_handler(401, req=req, error_override=error)
    #         else:
    #             payload = OrderedDict()
    #             payload['id'] = users[0]['id']
    #             payload['username'] = username
                
    #             data = jwt_payload_handler(payload)

    #             payload = {**payload, **data}

    #             self.on_success(res, payload)

        
    #     elif len(users) > 1:
    #         error = {
    #             'description': f"There was more than 1 user found for username: '{username}'"
    #         }
    #         LOG.error(error)
    #         raise generic_error_handler(401, req=req, error_override=error)

    #     else:
    #         error = {
    #             'description': 'either username or password is invalid'
    #         }
    #         LOG.error(error)
    #         raise generic_error_handler(401, req=req, error_override=error)

# @falcon.before(validate_jwt_token)



# Standard python libraries
# import falcon
# import uuid
# import json

# from contextlib import suppress

# from api.common import BaseResource
# from api.v1 import ScormResource
# from conf.config import COMPANY
# from middleware.jwt_authentication import validate_jwt_token
# from utils import log
# from utils.errors import generic_error_handler

# LOG = log.get_logger()

# def addGroupName(group_id, group_name):
#     return {"group_id": group_id, "group_name": group_name}

# class List(ScormResource):
#     """
#     Handle for endpoint: /v1/lo
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(List, self).__init__(**kwargs)
        
#     def get_lo_data(self, req):

#         LO_DIC = dict()
#         type_content = req.get_json('type_content', dtype=str, min=1, max=20)
#         if type_content != "course":
#             LO_DIC["title"] = req.get_json('title', dtype=str, min=1, max=800)
#         LO_DIC["subtitle"] = req.get_json('subtitle', dtype=str, default="")
#         LO_DIC["description"] = req.get_json('description', default="")
#         LO_DIC["training_minutes"] = req.get_json('training_minutes', default=None)
#         LO_DIC["is_active"] = req.get_json('is_active', dtype=bool, default=True)
#         LO_DIC["url"] = req.get_json('url', default="")
#         LO_DIC["thumbnail_url"] = req.get_json('thumbnail_url', default="")
#         LO_DIC["provider"] = req.get_json('provider')  # NEED LIST OF THEM
#         LO_DIC["created_by"] = req.jwt_user_id
#         LO_DIC["created_by_group_id"] = req.get_json('created_by_group_id', default=req.jwt_group_id)
#         LO_DIC["is_private"] = req.get_json('is_private', default=False)
#         LO_DIC["type"] = req.get_json('type_content', dtype=str, min=1, max=20)
#         LO_DIC["type_content"] = type_content
#         LO_DIC["enforce_seq"] = False
#         LO_DIC["publisher"] = req.get_json('publisher', default=None)
#         LO_DIC["authors"] = req.get_json('authors', default=None)
#         LO_DIC["data"] = req.get_json('data', default={})
#         LO_DIC["consumer_data"] = req.get_json('consumer_data')

#         return LO_DIC

#     def add_uac_data(self, LO_DIC):
#         if "uac" in LO_DIC["provider"]["id"]:
#             if 'display_options' not in LO_DIC["consumer_data"]:
#                 return {'display_options':{'is_archived': False,'is_reviewed': False}}
#             else:
#                 return {}
#         else:
#             return {}

#         return None

#     def check_content_type(self, res, value):

#         content_list = ["application",
#                         "article",
#                         "audio",
#                         "composition",
#                         "course",
#                         "image",
#                         "playlist",
#                         "text",
#                         "url",
#                         "video",
#                         "document",
#                         "file",
#                         "media"]

#         if value in content_list:
#             return True
#         else:
#             return False

#     @falcon.before(validate_jwt_token)
#     def on_get(self, req, res):

#         params={}
#         # params['is_media'] = True
#         params['provider'] = "chub"
#         # Copy the query parameters
#         get_query_params = req.params

#         for key in get_query_params:
#             if get_query_params[key] == 'media' :
#                 params['is_media'] = "True"
#             else:
#                 params[key] = get_query_params[key]

#         dl_content = self.datalayer.get(req, path=f"/learningobjects/", headers=self.headers, params=params)
#         self.on_success(res, dl_content)

#     @falcon.before(validate_jwt_token)
#     def on_post(self, req, res):

#         if not req.get_json_flag:
#             error = {
#                 'title': 'Syntax error',
#                 'description': f'Malformed JSON. method: {req.method}, url: {req.url}'
#             }
#             LOG.error(error)
#             raise generic_error_handler(400, req=req, error_override=error)

#         LO_DIC = self.get_lo_data(req)
#         LO_DIC['consumer_data'].update(self.add_uac_data(LO_DIC))

#         if "group" not in LO_DIC["consumer_data"] or LO_DIC["consumer_data"]["group"] is None:
#             LO_DIC["consumer_data"]["group"] = []

#         if not isinstance(LO_DIC["consumer_data"]["group"], list):  ## most preferred way to check if it's list
#             error = {
#                 'description': 'POST Group Error',
#                 'details': 'Group is not a list'
#             }
#             raise generic_error_handler(400, req=req, error_override=error)

#         if len(LO_DIC["consumer_data"]["group"]) < 1:
#             LO_DIC["consumer_data"]["group"] = [addGroupName(req.jwt_group_id, req.jwt_group_name)]
            
#         if not self.check_content_type(res, LO_DIC["type_content"]):
#             error = {
#                 'description': 'POST content_type Error',
#                 'details': f'content_type : {LO_DIC["type_content"]} is not valid'
#             }
#             raise generic_error_handler(400, req=req, error_override=error)
#         else:
#             #TODO: REMOVE collection AFTER INTUITION and front end have migrated over
#             collection = []
#             with suppress(Exception):
#                 for children_obj in LO_DIC["data"]["children"]:
#                     LOG.debug(children_obj.get("guid"))
#                     collection.append(children_obj.get("guid"))
                
#                 LO_DIC["data"]["collection"] = collection

#         if LO_DIC["type"] == "media":
#             with suppress(Exception):
#                 mime_type = LO_DIC["data"]["mime_type"].split("/")
#                 LO_DIC["type"]  = mime_type[0]
#                 LO_DIC["type_content"] = mime_type[0]

#         if LO_DIC["type"] == "playlist":
#             response_data_esapi = self.esapi.post(
#                 req, path=f"/{COMPANY}/{req.jwt_user_id}/user", headers=self.headers, json={})
#             first = response_data_esapi["results"]["_source"]["first_name"]
#             last = response_data_esapi["results"]["_source"]["last_name"]

#             LO_DIC["authors"]=f"{first} {last}"

#         with suppress(Exception):
#             if LO_DIC["type"] in ["playlist", "composition"]:
#                 enforce_seq = req.get_json('enforce_seq')
#                 if enforce_seq in [True, False]:
#                     LO_DIC["enforce_seq"] = enforce_seq

#         if LO_DIC["type"] == "course":

#             # Create an id
#             id_ = str(uuid.uuid4())
#             LO_DIC["data"]["course_id"] = id_

#             # Sign the url to give to scorm
#             presigned_url = LO_DIC["url"]

#             # LOAD SCORM
#             # 1. Post Scorm File get Job ID
#             job_id = self.load_scorm_package(req, id_, presigned_url)

#             # 2. Keep calling for results of Scorm processing.
#             course_title = self.check_scorm_status(req, job_id=job_id)
            
#             # 3 Get Preview URL
#             preview_url = self.get_preview(req, id_)
               
#             LO_DIC["data"]["preview_url"] = preview_url

#             LO_DIC["data"]["scorm_package"] = LO_DIC["url"].split("?")[0]

#             LO_DIC["url"] = ""

#             LO_DIC["title"] = course_title

#         dl_post_response = self.datalayer.post(req, path=f"/learningobjects/", headers=self.headers, json=LO_DIC)

#         self.on_success(res, dl_post_response)

# class Detail(BaseResource, BaseSpecific):
#     """
#     Handle for endpoint: /v1/lo/{guid}
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(Detail, self).__init__(**kwargs)

#     @falcon.before(validate_jwt_token)
#     def on_get(self, req, res, guid):
#         dl_content = self.datalayer.get(req, path=f"/learningobjects/{guid}", headers=self.headers)
#         self.on_success(res, dl_content)

#     @falcon.before(validate_jwt_token)
#     def on_patch(self, req, res, guid):

#         dl_content = self.datalayer.get(req, path=f"/learningobjects/{guid}", headers=self.headers)

#         LO_DIC = dict()
#         LO_DIC["title"] = req.get_json('title', default=dl_content["title"])
#         LO_DIC["subtitle"] = req.get_json('subtitle', default=dl_content["subtitle"])
#         LO_DIC["description"] = req.get_json('description', default=dl_content["description"])
#         LO_DIC["training_minutes"] = req.get_json('training_minutes', default=dl_content["training_minutes"])
#         LO_DIC["is_active"] = req.get_json('is_active', default=dl_content["is_active"])
#         LO_DIC["is_searchable"] = req.get_json('is_searchable', default=dl_content["is_searchable"])
#         LO_DIC["url"] = req.get_json('url', default=dl_content["url"])
#         LO_DIC["thumbnail_url"] = req.get_json('thumbnail_url', default=dl_content["thumbnail_url"])

#         # ADDING A Edit user to pass to DTL
#         LO_DIC["editor"] = req.jwt_user_id
#         LO_DIC["editor_group"] = req.jwt_group_id
#         LO_DIC["edited_fields"] = req.get_json('edited_fields', default="")

#         # TODO: REMOVE THIS LOGIC WHEN WE DEPRICATE TYPE
#         if dl_content["type_content"]:
#             LO_DIC["type"] = req.get_json('type_content', default=dl_content["type_content"])
#             LO_DIC["type_content"] = req.get_json('type_content', default=dl_content["type_content"])
#         else:
#             LO_DIC["type"] = req.get_json('type_content', default=dl_content["type"])
#             LO_DIC["type_content"] = req.get_json('type_content', default=dl_content["type"])

#         # TODO: REMOVE collection AFTER intuition and front end have migrated over
#         collection = []
#         with suppress(Exception):
#             for children_obj in LO_DIC["data"]["children"]:
#                 collection.append(children_obj.get("guid"))

#             LO_DIC["data"]["collection"] = collection

#         with suppress(Exception):
#             if LO_DIC["type_content"] in ["playlist", "composition"]:
#                 enforce_seq = req.get_json('enforce_seq')
#                 if enforce_seq in [True, False]:
#                     LO_DIC["enforce_seq"] = enforce_seq
        
#         with suppress(Exception):
#             mime_type = LO_DIC["data"]["mime_type"].split("/")
#             LO_DIC["type"] = mime_type[0]
#             LO_DIC["type_content"] = mime_type[0]

#         # TODO: MAKE A LIST of approval
#         LO_DIC["provider"] = req.get_json('provider', default=dl_content["provider"])

#         # WE don't CHANGE once it is created
#         # LO_DIC.created_by = "" #JWT-->GUID
#         LO_DIC["created_by_group_id"] = req.get_json('created_by_group_id', default=dl_content["created_by_group_id"])

#         #TODO: Playlist uses this only
#         LO_DIC["is_private"] = req.get_json('is_private', default=dl_content["is_private"])

#         LO_DIC["publisher"] = req.get_json('publisher', default=dl_content["publisher"])
#         LO_DIC["authors"] = req.get_json('authors', default=dl_content["authors"])

#         # NEED TO PASS THE FULL OBJECT
#         LO_DIC["data"] = req.get_json('data', default=dl_content["data"])
#         LO_DIC["consumer_data"] = req.get_json('consumer_data', default=dl_content["consumer_data"])

#         if "group" in LO_DIC["consumer_data"] and not isinstance(LO_DIC["consumer_data"]["group"], list):  ## most preferred way to check if it's list
#             error = {
#                 'description': 'PATCH Group Error',
#                 'details': 'Group is not a list'
#             }
#             raise generic_error_handler(400, req=req, error_override=error)

#         # if len(LO_DIC["consumer_data"]["group"]) < 1:
#         #     LO_DIC["consumer_data"]["group"] = [addGroupName(req.jwt_group_id, req.jwt_group_name)]

#         dl_patch_response = self.datalayer.patch(req, path=f"/learningobjects/{guid}", headers=self.headers, json=LO_DIC)

#         # Add EDIT LOG FOR ALL PATCHES
#         cts_body = {
#             "media_id": guid,
#             "edited_fields": req.get_json('edited_fields', default=""),
#             "editor" : req.jwt_user_id,
#             "editor_group":req.jwt_group_id
#         }
#         self.headers["Authorization"] = req.jwt_token
#         _ = self.datalayer.post(req, path="/edit_log/", headers=self.headers, json=cts_body)

#         self.on_success(res, dl_patch_response)

#     @falcon.before(validate_jwt_token)
#     def on_delete(self, req, res, guid):

#         # Checking if it exists. If not, it raises error
#         _ = self.datalayer.get(req, path=f"/learningobjects/{guid}", headers=self.headers)

#         LO_DIC = {"is_active": False}

#         dl_patch_response = self.datalayer.patch(req,
#                                                 path=f"/learningobjects/{guid}",
#                                                 headers=self.headers,
#                                                 json=LO_DIC)

#         self.on_success(res, dl_patch_response)

# class Copy_LO(BaseResource, BaseSpecific):
#     """
#     Handle for endpoint: /v1/lo/{guid}/copy
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(Copy_LO, self).__init__(**kwargs)

#     @falcon.before(validate_jwt_token)
#     def on_get(self, req, res, guid):
#         raise generic_error_handler(500, req=req)

#     @falcon.before(validate_jwt_token)
#     def on_post(self, req, res, guid):

#         dl_content = self.datalayer.get(req, path=f"/learningobjects/{guid}", headers=self.headers)

#         # Change Owner
#         dl_content["created_by"] = req.jwt_user_id
#         dl_content["created_by_group_id"] = req.jwt_group_id

#         response_data_esapi = self.esapi.post(req, path=f"/{COMPANY}/{req.jwt_user_id}/user",
#                                                     headers=self.headers,
#                                                     json={})
#         first = response_data_esapi["results"]["_source"]["first_name"]
#         last = response_data_esapi["results"]["_source"]["last_name"]

#         dl_content["authors"] = f"{first} {last}"

#         del dl_content['guid']
#         del dl_content['external_guid']
#         del dl_content['parent_guid_path']
#         del dl_content['external_id']

#         del dl_content['location']
#         del dl_content['version']
#         del dl_content['is_current_version']
#         del dl_content['loid_first_version']
#         del dl_content['default_language']
#         del dl_content['training_minutes']
#         del dl_content['training_credits']

#         del dl_content['is_new_flag']
#         del dl_content['is_cpe_flag']
#         del dl_content['attendance_parts']
#         del dl_content['minimum_user_registration']
#         del dl_content['maximum_user_registration']

#         del dl_content['date_starts']
#         del dl_content['date_ends']
#         del dl_content['timezone']
#         del dl_content['part_break']

#         del dl_content['provider']['type']
#         del dl_content['provider']['name']
#         del dl_content['provider']['is_writable']
#         del dl_content['provider']['is_transcript_writable']
#         del dl_content['provider']['is_chub_like']

#         del dl_content['rating_avg']
#         del dl_content['rating_count']
#         del dl_content['comment_count']
#         del dl_content['subscriber_count']
#         del dl_content['date_created']
#         del dl_content['date_imported']
#         del dl_content['date_modified']
#         del dl_content['organizations']
#         del dl_content['children']

#         if not dl_content['data']:
#             dl_content['data'] = dict()

#         #type_content
#         if not dl_content['type_content']:
#             dl_content['type_content'] = dl_content['type']

#         dl_post_response = self.datalayer.post(req, path="/learningobjects/", headers=self.headers, json=dl_content)
#         self.on_success(res, dl_post_response)

# class Subscribe_LO(BaseResource, BaseSpecific):
#     """
#     Handle for endpoints: 
#     /v1/lo/{guid}/subscribe
#     /v1/lo/{guid}/subscribe/{list}
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(Subscribe_LO, self).__init__(**kwargs)

#     @falcon.before(validate_jwt_token)
#     def on_get(self, req, res, guid, list=None):

#         params = dict()
#         #TODO: WHAT IS THIS FLAG FOR
#         if not list:
#             params["user_guid"] = req.jwt_user_id
#         params["loid"] = guid

#         dl_content = self.datalayer.get(req, path="/subscriptions/", headers=self.headers, params=params)
#         self.on_success(res, dl_content)

#     @falcon.before(validate_jwt_token)
#     def on_post(self, req, res, guid, list=None):
#         payload = {
#             "user_guid": req.jwt_user_id,
#             "loid": guid
#         }
#         dl_content_get = self.datalayer.get(req, path="/subscriptions/", headers=self.headers, params=payload)

#         # TODO: Check this two different responses (lines 323 and 328)
#         if dl_content_get["count"] == 1:
#             error = {
#                 'description': f'subscription with client ID "{req.jwt_user_id}" already exist.'
#             }
#             raise generic_error_handler(409, req=req, error_override=error)
#         else:
#             dl_content = self.datalayer.post(
#                 req, 
#                 path="/subscriptions/", 
#                 headers=self.headers,
#                 json=payload)
#             self.on_success(res, dl_content)

#     @falcon.before(validate_jwt_token)
#     def on_delete(self, req, res, guid, list=None):
#         get_path = "/subscriptions/"

#         params = {
#             "user_guid": req.jwt_user_id,
#             "loid": guid
#         }

#         dl_content_get = self.datalayer.get(req, path="/subscriptions/", headers=self.headers, params=params)

#         if dl_content_get["count"] == 1:
#             subscriptions_id = dl_content_get["results"][0]["id"]
#             l_content_get = self.datalayer.delete(req, path=f"/subscriptions/{subscriptions_id}/", headers=self.headers)
#             self.on_no_content(res, {})

#         else:
#             error = {
#                 'description': f"subscription with client ID '{req.jwt_user_id}' does not exist."
#             }
#             raise generic_error_handler(404, req=req, error_override=error)
        
# class ScormLaunchLink(ScormResource):
#     """
#     Handle for endpoint: /v1/healthcheck
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(ScormLaunchLink, self).__init__(**kwargs)

#     @falcon.before(validate_jwt_token)
#     def on_get(self, req, res, guid, list=None):

#         self.on_success(res, {})

# class SCORM_UPLOAD(ScormResource):
#     """
#     Handle for endpoint: /v1/healthcheck
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(SCORM_UPLOAD, self).__init__(**kwargs)

#     def get_base_fields(self, req):
#         LO_DIC = dict()
#         LO_DIC["type_content"] = req.get_json('type_content', dtype=str, min=1, max=20)
#         if LO_DIC["type_content"] != "course":
#             LO_DIC["title"] = req.get_json('title', dtype=str, min=1, max=800)
#         LO_DIC["enforce_seq"] = False
#         LO_DIC["subtitle"] = req.get_json('subtitle', dtype=str, default="")
#         LO_DIC["description"] = req.get_json('description', default="")
#         LO_DIC["training_minutes"] = req.get_json('training_minutes', default=1)
#         LO_DIC["is_active"] = req.get_json('is_active', dtype=bool, default=True)
#         LO_DIC["url"] = req.get_json('url', default="")
#         LO_DIC["thumbnail_url"] = req.get_json('thumbnail_url', default="")
#         LO_DIC["provider"] = req.get_json('provider')  # NEED LIST OF THEM
#         LO_DIC["created_by"] = req.jwt_user_id
#         LO_DIC["created_by_group_id"] = req.jwt_group_id
#         LO_DIC["is_private"] = req.get_json('is_private', default=False)
#         # TODO: REMOVE ONCE 2.4
#         LO_DIC["type"] = req.get_json('type_content', dtype=str, min=1, max=20)
        
#         LO_DIC["publisher"] = req.get_json('publisher', default=None)
#         LO_DIC["authors"] = req.get_json('authors', default=None)
#         LO_DIC["data"] = req.get_json('data', default={})
#         LO_DIC["consumer_data"] = req.get_json('consumer_data')

#         return LO_DIC

#     @falcon.before(validate_jwt_token)
#     def on_post(self, req, res):
        
#         lo_obj = self.get_base_fields(req)

#         if lo_obj["type_content"] == "course":

#             # Create an id
#             id_ = str(uuid.uuid4())
#             lo_obj["data"]["course_id"] = id_

#             # Sign the url to give to scorm
#             presigned_url = lo_obj["url"]

#             # LOAD SCORM
#             # 1. Post Scorm File get Job ID
#             job_id = self.load_scorm_package(req, id_, presigned_url)

#             # 2. Keep calling for results of Scorm processing.
#             course_title = self.check_scorm_status(req, job_id=job_id)
            
#             # 3 Get Preview URL
#             preview_url = self.get_preview(req, id_)
               
#             lo_obj["data"]["preview_url"] = preview_url

#             lo_obj["data"]["scorm_package"] = lo_obj["url"].split("?")[0]

#             lo_obj["url"] = ""

#             lo_obj["title"] = course_title

#             dl_post_response = self.datalayer.post(req, path=f"/learningobjects/", headers=self.headers, json=lo_obj)

#         self.on_success(res, dl_post_response)

# class ScormUploadBackend(ScormResource):
#     """
#     Handle for endpoint: /v1/healthcheck
#     """
#     def __init__(self, **kwargs):
#         """ Creates a client instance """
#         super(ScormUploadBackend, self).__init__(**kwargs)

#     def get_base_fields(self, req):
#         LO_DIC = dict()
        
#         # =========
#         # Required
#         # =========
#         missing_fields = []
#         required_fields = ['type_content', 'provider', 'consumer_data']
#         for required_field in required_fields:
#             if required_field not in req.params:
#                 missing_fields.append(required_field)
#             else:
#                 if required_field in ['provider', 'consumer_data']:
#                     try:
#                         LO_DIC[required_field] = json.loads(req.params[required_field])
#                     except Exception as ex:
#                         error = {
#                             'description': f'Invalid JSON format in form field {required_field}',
#                             'details': f'{ex}'}
#                         raise generic_error_handler(400, req=req, error_override=error)
#                 else:
#                     LO_DIC[required_field] = req.params[required_field]
        
#         if missing_fields:
#             error = {
#                 'description': 'Missing required fields',
#                 'details': f'missing fields: {missing_fields}'}
#             raise generic_error_handler(400, req=req, error_override=error)

#         # TODO: REMOVE ONCE 2.4
#         LO_DIC["type"] = LO_DIC["type_content"]
        
#         # ===============
#         # Default Values
#         # ===============
#         default_values = {
#             'enforce_seq': False,
#             'subtitle': '',
#             'description': '',
#             'training_minutes': 1,
#             'is_active': True,
#             'url': '',
#             'thumbnail_url': '',
#             'is_private': False,
#             'publisher': None,
#             'authors': None,
#             'data': {}
#         }

#         for k in default_values:
#             if k not in req.params:
#                 LO_DIC[k] = default_values[k]
#             else:
#                 LO_DIC[k] = req.params[k]

#         return LO_DIC

#     def get_aws_file_id(self, url):

#         file_name = url.split("/")[-1]
#         file_data = {
#             "name":file_name,
#             "id": file_name.split(".")[0]
#         }

#         return file_data

#     @falcon.before(validate_jwt_token)
#     def on_post(self, req, res):
#         # 1. Add object to AWS
#         if "multipart/form-data" not in req.content_type:
#             raise falcon.HTTPUnsupportedMediaType(
#                 f"This view only allows content_type 'multipart/form-data', not '{req.content_type}'")

#         try:
#             if 'file' not in req.params:  
#                 raise Exception('Missing File')
#             if req.params['file'] == "":
#                 raise Exception('Missing File')
#             scorm_file = req.get_param('file').value
#         except Exception as ex:
#             error = {'description': f'{ex}'}
#             raise generic_error_handler(400, req=req, error_override=error)
         
         
#         lo_obj = self.get_base_fields(req)
        
#         # We need to auto create an id for the course
#         course_id = str(uuid.uuid4())
#         response = self.aws_client.add_new_zip(name=course_id, course=scorm_file)

#         # 2. Sign URL with id of object from AWS
#         location = response["location"]

#         if lo_obj["type_content"] == "course":

#             # Get the aws url and brake it apart
#             aws_file_data = self.get_aws_file_id(location)
#             # id_ = str(uuid.uuid4())
#             lo_obj["data"]["course_id"] = aws_file_data['id']

#             # Sign the url to give to scorm
#             presigned_url = self.aws_client.create_presigned_url(req, obj_id=aws_file_data["id"])

#             if 'only_presigned_url' in req.params:
#                 lo_FE = {
#                     "provider": lo_obj["provider"],
#                     "type_content": lo_obj["type_content"],
#                     "url": presigned_url,
#                     "courseName": lo_obj["data"]["course_id"],
#                     "consumer_data": lo_obj["consumer_data"]
#                 }
                
#                 res.status = falcon.HTTP_200
#                 res.json = lo_FE
        
#             else:
#                 # LOAD SCORM
#                 # 1. Post Scorm File get Job ID
#                 job_id = self.load_scorm_package(req, aws_file_data['id'], presigned_url)
                
#                 # 2. Keep calling for results of Scorm processing.
#                 course_title = self.check_scorm_status(req, job_id=job_id)
                
#                 # 3 Get Preview URL
#                 preview_url = self.get_preview(req, aws_file_data['id'])
                
#                 lo_obj["data"]["preview_url"] = preview_url

#                 lo_obj["data"]["scorm_package"] = lo_obj["url"].split("?")[0]

#                 lo_obj["url"] = ""

#                 lo_obj["title"] = course_title

#                 # dl_post_response = self.DataLayerClient.post(req, path=f"/learningobjects/", headers=self.header, json=lo_obj)

#                 self.on_success(res, lo_obj)
