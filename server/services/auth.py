import functools
import hashlib
import hmac
import os

from flask import request, abort

SLACK_SIGNING_SECRET = os.environ.get('SLACK_SECRET')


def slack_auth_required(handler):
    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        req_signature = request.headers.get('X-Slack-Signature')
        body = request.get_data(as_text=True)
        timestamp_header = request.headers.get('X-Slack-Request-Timestamp')
        sig_basestring = 'v0:' + timestamp_header + ':' + body
        comp_signature = 'v0=' + hmac.new(SLACK_SIGNING_SECRET.encode(), sig_basestring.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(comp_signature, req_signature):
            return handler(*args, **kwargs)
        else:
            abort(401)

    return wrapper
