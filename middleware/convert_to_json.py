# Standard python libraries
import uuid
from datetime import datetime
import json
import re
import cgi
from io import BytesIO
# Third party libraries: requirements.txt
import six

# Resources created in other modules of app.
from utils.errors import generic_error_handler

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

class ConvertToJson(object):
    def __init__(self, help_messages=True):
        """help_messages: display validation/error messages"""
        self.debug = bool(help_messages)
        self.parser = cgi.FieldStorage

    def parse_field(self, field):
        if isinstance(field, list):
            return [self.parse_field(subfield) for subfield in field]

        # When file name isn't ascii FieldStorage will not consider it.
        encoded = field.disposition_options.get('filename*')
        if encoded:
            # http://stackoverflow.com/a/93688
            encoding, filename = encoded.split("''")
            field.filename = filename
            # FieldStorage will decode the file content by itself when
            # file name is encoded, but we need to keep a consistent
            # API, so let's go back to bytes.
            # WARNING we assume file encoding will be same as filename
            # but there is no guaranty.
            field.file = BytesIO(field.file.read().encode(encoding))
        if getattr(field, 'filename', False):
            return field
        # This is not a file, thus get flat value (not
        # FieldStorage instance).
        return field.value

    def check_json(self, field):
        return True if field in self.req.json else False

    def get_json(self, field, **kwargs):
        """Helper to access JSON fields in the request body

        Optional built-in validators.
        """
        value = None
        if field in self.req.json:
            value = self.req.json[field]
            kwargs.pop('default', None)
        elif 'default' not in kwargs:
            error = {
                'description': 'Missing JSON field',
                'details': f"Field '{field}' is required"}
            raise generic_error_handler(400, error_override=error)
        else:
            value = kwargs.pop('default')

        validators = kwargs
        return self.validate(field, value, **validators)

    # TODO replace this with https://github.com/Julian/jsonschema
    def validate(self, field, value, dtype=None, default=None, min=None, max=None, match=None, choices=None, valid_uuid=None):
        """JSON field validators:

        dtype      data type
        default    value used if field is not provided in the request body
        min        minimum length (str) or value (int, float)
        max        maximum length (str) or value (int, float)
        match      regular expression
        choices    list to which the value should be limited
        """
        err_title = "Validation error"

        if dtype:
            if type(value) is not dtype:
                error = {
                    "title": err_title,
                    "description": f"Data type for '{field}' is '{type(value).__name__}' but should be '{dtype.__name__}'"}
                raise generic_error_handler(400, error_override=error)

        if type(value) in six.string_types:
            if min and len(value) < min:
                error = {
                    "title": err_title,
                    "description": f"Minimum length for '{field}' is '{min}'"}
                raise generic_error_handler(400, error_override=error)

            if max and len(value) > max:
                error = {
                    "title": err_title,
                    "description": f"Maximum length for '{field}' is '{max}'"}
                raise generic_error_handler(400, error_override=error)

        elif type(value) in (int, float):
            if min and value < min:
                error = {
                    "title": err_title,
                    "description": f"Minimum length for '{field}' is '{min}'"}
                raise generic_error_handler(400, error_override=error)

            if max and value > max:
                error = {
                    "title": err_title,
                    "description": f"Maximum length for '{field}' is '{max}'"}
                raise generic_error_handler(400, error_override=error)

        if match and not re.match(match, re.escape(value)):
            error = {
                "title": err_title,
                "description": f"'{field}' does not match Regex: {match}"}
            raise generic_error_handler(400, error_override=error)

        if valid_uuid:
                try:
                    uuid.UUID(value).hex
                except ValueError:
                    error = {
                        "title": err_title,
                        "description": f"'{field}' is Not a valid UUID: {value}"}
                    raise generic_error_handler(400, error_override=error)

        if choices and value not in choices:
            error = {
                "title": err_title,
                "description": f"{field} must be one of {choices}"}
            raise generic_error_handler(400, error_override=error)

        return value

    def process_request(self, req, resp):
        """Middleware request"""
        if not req.content_length:
            req.get_json_flag = False
            if req.method in ['POST', 'PUT', 'PATCH']:
                # body = '{}'.encode('utf-8')
                error = {
                    "description": "No payload in request",
                    "details": "If no payload intended, please pass '{}' in payload"
                }
                raise generic_error_handler(400, error_override=error)
            else:
                return

        if 'application/json' in req.content_type:
            body = req.stream.read()
            req.json = {}
            self.req = req
            req.get_json_flag = True
            req.get_json = self.get_json  # helper function
            req.check_json = self.check_json  # helper function

            try:
                req.json = json.loads(body.decode('utf-8'))
            except UnicodeDecodeError:
                error = {
                    "description": "Invalid encoding",
                    "details": "Could not decode as UTF-8"}
                raise generic_error_handler(400, error_override=error)
            except ValueError:
                error = {
                    "description": "Malformed JSON",
                    "details": "Syntax error"
                }
                raise generic_error_handler(400, error_override=error)

        elif "multipart/form-data" in req.content_type:
            # Multipart
            # https://github.com/falconry/falcon/issues/886
            # https://github.com/yohanboniface/falcon-multipart

            # This must be done to avoid a bug in cgi.FieldStorage.
            req.env.setdefault('QUERY_STRING', '')
            try:
                form = self.parser(fp=req.stream, environ=req.env)
            except ValueError as e:  # Invalid boundary?
                error = {
                    "description": "Error parsing file",
                    "details": str(e)
                }
                raise generic_error_handler(400, error_override=error)

            for key in form:
                # TODO: put files in req.files instead when #418 get merged.
                # noinspection PyProtectedMember
                req._params[key] = self.parse_field(form[key])
        else:
            # return None
            return

    def process_response(self, req, resp, resource, req_succeeded):
        """Middleware response"""
        if getattr(resp, "json", None) is not None:
            resp.body = str.encode(json.dumps(resp.json, cls=DateTimeEncoder))
