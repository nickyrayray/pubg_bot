from flask import jsonify


def do_request_verification(request_body):
    resp = jsonify({
        'challenge': request_body.get('challenge')
    })
    resp.status_code = 200
    return resp


def is_someone_bad(name_or_username):
    pass