import functools
from hmac import compare_digest
from flask import request,jsonify
import config


def is_valid(api_key):
    device = config.API_KEY
    if device and (device ==  api_key):
        return True


def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401

        # Check if API key is correct and valid
        if request.method == "POST" and is_valid(token):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator