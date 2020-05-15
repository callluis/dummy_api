# -*- coding: utf-8 -*-

import falcon
import json

from conf.config import APP_NAME, LOG
from utils.errors import generic_error_handler

class BaseResource(object):
    BASE_TEMPLATE = {
        'server': '%s' % APP_NAME
    }

    def to_json(self, body_dict):
        return json.dumps(body_dict)

    def on_created(self, res, data=None):
        res.status = falcon.HTTP_201
        meta = {
            'code': 201,
            'message': 'created',
        }
        # res.body = self.to_json(obj)
        res.json = {'meta': meta, 'data': data}

    def on_success(self, res, data=None):
        res.status = falcon.HTTP_200
        meta = data.get('meta') or {}
        meta['code'] = 200
        meta['message'] = 'OK'
        data['meta'] = meta
        res.json = data

    def on_no_content(self, res, data=None):
        res.status = falcon.HTTP_204
        meta = {
            'code': 204,
            'message': 'No Content'
        }
        data = {} if not data else data
        data['meta'] = meta
        res.json = data

    def on_paginate(self, res, data_dic=None):
        res.status = falcon.HTTP_200
        data_dic['meta'] = {
            'code': 200,
            'message': 'OK'
        }
        res.json = data_dic

    def on_get(self, req, res, **kwargs):
        if req.path in ['/', '/healthcheck']:
            res.status = falcon.HTTP_200
            data = self.BASE_TEMPLATE
            meta = {
                'code': 200,
                'message': 'OK'
            }
            data['meta'] = meta
            res.json = data
        else:
            raise generic_error_handler(500, req=req)

    def on_post(self, req, res, **kwargs):
        raise generic_error_handler(405, req=req)

    def on_put(self, req, res, **kwargs):
        raise generic_error_handler(405, req=req)

    def on_patch(self, req, res, **kwargs):
        raise generic_error_handler(405, req=req)

    def on_delete(self, req, res, **kwargs):
        raise generic_error_handler(405, req=req)
