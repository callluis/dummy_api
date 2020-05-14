# -*- coding: utf-8 -*-
# Standard python libraries
import json
# Third party libraries: equirements.txt
import falcon
from falcon.http_error import HTTPError
# Resources created in other modules of app.
from conf.config import STATUS_MAPPING, APP_NAME

def generic_path_error_handler(req, res):
    res.status = falcon.HTTP_404
    path = req.path
    meta = {
        'code': 404,
        'title': 'resource not found',
        'description': f'resource not found: {req.path}',
        'details': f'method: {req.method}, url: {path} not found'}
    res.json = {'meta': meta}  # Python 3

def generic_error_handler(status_code, req=None, error_override=None):
    error_override = error_override if error_override else {}
    
    req_attributes = ['path', 'method']
    error_data = {}

    for attribute in req_attributes:
        if hasattr(req, attribute):
            error_data[attribute] = getattr(req, attribute)
        else:
            error_data[attribute] = 'not_specified'

    ERRORS = {
        400: {
            'title': 'bad request',
            'description': 'invalid request',
        },
        401: {
            'title': 'unauthorized',
            'description': 'unauthorized to consume this resource'
        },
        404: {
            'title': 'resource not found',
            'description': f'resource not found: {error_data["path"]}'
        },
        405: {
            'title': 'method not allowed',
            'description': f'{error_data["method"]} is not allowed for this endpoint: {error_data["path"]}'
        },
        500: {
            'title': 'not supported',
            'description': f'method: {error_data["method"]}, url: {error_data["path"]} not supported'
        }
    }

    meta = {'code': status_code}

    if ERRORS.get(status_code):
        meta['title'] = error_override.get('title') or ERRORS[status_code].get('title')
        meta['description'] = error_override.get('description') or ERRORS[status_code].get('description')
    else:
        meta['title'] = error_override.get('title') or 'generic error'
        description = error_override.get('description')
        if description:
            meta['description'] = description

    details = error_override.get('details')
    if details:
        meta['details'] = details

    service = error_override.get('service') or APP_NAME

    raise CustomeHTTPError(STATUS_MAPPING[status_code], {"service": service, "meta": meta})

#*******************************************************
class CustomeHTTPError(HTTPError):

    """
    Represents a generic HTTP error.
    """

    def __init__(self, status, error):
        super(CustomeHTTPError, self).__init__(status)
        self.status = status
        self.error = error

    def to_dict(self, obj_type=dict):
        """Returns a basic dictionary representing the error.
        """
        super(CustomeHTTPError, self).to_dict(obj_type)
        obj = self.error
        return obj
