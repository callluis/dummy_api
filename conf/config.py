# -*- coding: utf-8 -*-
import os
import logging
from falcon import status_codes

# =============================================================================
# Initialization
# =============================================================================
APP_NAME = 'Dummy API'

# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================
API_SECRET_KEY = os.environ.get('API_SECRET_KEY', 'whatever')
SUPER_ADMIN_KEY = os.environ.get('SUPER_ADMIN_KEY', 'SUPER')

# =============================================================================
# Logging
# =============================================================================
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

# =============================================================================
# DATABASE
# =============================================================================
# Setting up the database
DATABASE = "db/data.db"

# =============================================================================
# MAPPER to catch regular status_codes (ex.: 404) and convert it
# to valid falcon status_codes (ex.: falcon.HTTP_404)
# =============================================================================
STATUS_MAPPING = {}
for attr in dir(status_codes):
    if not attr.startswith('HTTP_'):
        continue
    try:
        http_status = attr.split('_')[1]
        http_status = int(http_status)
    except ValueError:
        continue

    STATUS_MAPPING[http_status] = getattr(status_codes, attr)
