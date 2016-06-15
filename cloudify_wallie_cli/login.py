# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json


def login_to_openstack(logger, user, password, auth_url, tenant_name, wallie_host):
    payload = {
        "user": user,
        "password": password,
        "auth_url": auth_url,
        "tenant_name": tenant_name
    }
    r = requests.post(wallie_host + '/login_openstack', data=json.dumps(payload))
    if r.status_code == 200:
        return json.loads(r.content) ['x-openstack-authorization']
    return None
