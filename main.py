# -*- coding: utf-8 -*-

import falcon

from api.common import base
from api.v1 import astronauts, users
from conf.config import APP_NAME, LOG
from db import init_session
from middleware import ConvertToJson, RequireJSON
from utils.errors import generic_path_error_handler

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info(f'Starting {APP_NAME}')
        self.add_route('/', base.BaseResource())
        
        # Users
        self.add_route('/api/users', users.Users())
        self.add_route('/api/users/{user_id}', users.Users())
        # self.add_route('/api/login', d4uth.Login())
        
        # Astronauts
        # self.add_route('/api/astronauts', astronauts.List())
        # self.add_route('/api/astronauts/{id_}', astronauts.Detail())

        # This catches none existing paths
        self.add_sink(generic_path_error_handler, '')

        # This is needed starting in Falcon 2.0 (where the default value changed
        # from `True` to `False`).
        self.req_options.strip_url_path_trailing_slash = True

init_session()
middleware = [ConvertToJson(help_messages=True), RequireJSON()]
application = App(middleware=middleware)
