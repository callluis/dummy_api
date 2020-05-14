import hashlib
import random
import string

def making_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_password_hashing(password, salt=None):
    if not salt:
        salt = making_salt()
    hash_ = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return f'{hash_},{salt}'

def checking_password_hash(password, hash_):
    salt = hash_.split(',')[1]
    if make_password_hashing(password, salt) == hash_:
        return True
    return False
