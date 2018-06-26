import requests
import sys
from websocket import create_connection


def ws_create():
    login_data = {
        'User': {
            'login_id': 'admin',
            'password': 'SlvAtu$2018'
        }
    }

    r = requests.post(
        'http://192.168.1.28/api/login',
        json=login_data)

    print('Status: %s' % r.status_code, file=sys.stderr)
    print('Text: %s' % r.text, file=sys.stderr)

    res = r.json()

    print('Response: %s - %s' % (res['Response']['code'], res['Response']['message']), file=sys.stderr)
    print('Session id.: %s  ' % r.headers['bs-session-id'], file=sys.stderr)

    ws = create_connection('ws://192.168.1.28/wsapi')
    ws.send('bs-session-id=%s' % r.headers['bs-session-id'])
    result = ws.recv()
    print("Received '%s'" % result, file=sys.stderr)
    # ws.close()

    r2 = requests.post(
        'http://192.168.1.28/api/events/start',
        json={},
        headers={'bs-session-id': r.headers['bs-session-id']})

    print('Status: %s' % r2.status_code, file=sys.stderr)
    print('Text: %s' % r2.text, file=sys.stderr)

    return r.headers['bs-session-id']
