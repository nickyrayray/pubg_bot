from flask import jsonify

GOOD_QUESTION_REGEX = 'am|is (\S+) (good|bad)'
DEFAULT_RESPONSE = 'WHAT THE *ACTUAL FUCK* ARE YOU _EVEN_ TALKING ABOUT???'


def do_request_verification(request_body):
    resp = jsonify({
        'challenge': request_body.get('challenge')
    })
    resp.status_code = 200
    return resp


def handle_event_response(event, **_):
    response = {'channel': event.get('channel'), 'text': 'test response'}
    event_type = event.get('type')
    if event_type == 'app_mention':
        response.update(_handle_app_mention(event.get('text')))
    else:
        response.update(_get_default_response())
    return response


def _get_default_response():
    return {
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': DEFAULT_RESPONSE
                }
            }
        ]
    }


def _handle_app_mention(text):
    return _get_default_response()

