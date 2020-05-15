from collections import OrderedDict
import datetime
import jwt

from conf.config import JWT_EXPIRATION_SECONDS, API_SECRET_KEY

def jwt_payload_handler(payload):

    # data = OrderedDict()
    data = {}
    data['id'] = payload['id']
    data['username'] = payload['username']
    data['foo'] = 'bar'

    data['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION_SECONDS)

    readable_time = (data['exp'])

    response = {
        'jwt': jwt.encode(data, API_SECRET_KEY, 'HS256').decode('utf-8'),
        'expires_at': readable_time.strftime('%Y-%m-%d %H:%M:%S')
    } 

    return response
