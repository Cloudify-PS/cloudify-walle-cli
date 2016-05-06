import requests
import json


def login_to_openstack(logger, user, password, auth_url, tenant_name, score_host):
    payload = {
        "user": user,
        "password": password,
        "auth_url": auth_url,
        "tenant_name": tenant_name
    }
    r = requests.post(score_host + '/login_openstack', data=json.dumps(payload))
    if r.status_code == 200:
        return json.loads(r.content) ['x-openstack-authorization']
    return None
