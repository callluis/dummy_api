from utils.errors import generic_error_handler

class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            error = {"description": "This API only supports responses encoded as JSON."}
            raise generic_error_handler(400, req=req, error_override=error)

        if req.method not in ('OPTIONS') and req.method not in ('GET') and req.method not in ('DELETE'):
            if not req.content_type:
                error = {
                    "title": "Unsupported media type",
                    "description": "Malformed JSON"}
                raise generic_error_handler(415, req=req, error_override=error)
            elif "multipart/form-data" not in req.content_type:
                if 'application/json' not in req.content_type:
                    error = {
                        "title": "Unsupported media type",
                        "description": "Missing required header",
                        "details": {"choices" :["multipart/form-data", "application/json"]}}
                    raise generic_error_handler(415, req=req, error_override=error)
