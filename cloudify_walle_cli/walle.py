# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
# Copyright (c) 2015 VMware, Inc. All Rights Reserved.
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
import os
import tempfile
import shutil
import tarfile
import urllib

from os.path import expanduser
from dsl_parser import parser


class WalleException(Exception):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


def _check_exception(logger, response):
    if response.status_code != requests.codes.ok:
        logger.error('ERROR %s' % (response.content))
        raise WalleException(response.content)


class Walle(object):

    def __init__(self, url, auth_url=None, token=None,
                 region=None, tenant=None, verify=True, logger=None):
        self.url = url
        self.auth_url = auth_url
        self.token = token
        self.verify = verify
        self.region = region
        self.tenant = tenant
        self.response = None
        self.blueprints = BlueprintsClient(self, logger)
        self.deployments = DeploymentsClient(self, logger)
        self.executions = ExecutionsClient(self, logger)
        self.events = EventsClient(self, logger)
        self.endpoints = EndpointsClient(self, logger)
        self.tenants = TenantsClient(self, logger)
        self.limits = TenantLimitsClient(self, logger)
        self.logger = logger

    def get_headers(self):
        headers = {}
        headers["x-openstack-authorization"] = self.token
        headers["x-openstack-keystore-url"] = self.auth_url
        headers["x-openstack-keystore-region"] = self.region
        headers["x-openstack-keystore-tenant"] = self.tenant
        return headers

    def get_status(self):
        self.response = requests.get(
            self.url + '/status', headers=self.get_headers(),
            verify=self.verify
        )
        return self.response.content


class BaseClient(object):

    def __init__(self, walle, logger=False):
        self.walle = walle
        self.logger = logger

    def _get(self, path, params=None, json_request=True):
        headers = self.walle.get_headers()
        if json_request:
            headers['Content-type'] = 'application/json'
        self.walle.response = requests.get(
            self.walle.url + path,
            headers=headers,
            params=params,
            verify=self.walle.verify
        )
        _check_exception(self.logger, self.walle.response)
        return json.loads(self.walle.response.content)

    def _update(self, path, data):
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.put(
            self.walle.url + path,
            headers=headers, data=json.dumps(data),
            verify=self.walle.verify
        )
        _check_exception(self.logger, self.walle.response)
        return json.loads(self.walle.response.content)

    def _add(self, path, data):
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.post(
            self.walle.url + path,
            headers=headers, data=json.dumps(data),
            verify=self.walle.verify
        )
        _check_exception(self.logger, self.walle.response)
        return json.loads(self.walle.response.content)

    def _delete(self, path):
        self.walle.response = requests.delete(
            self.walle.url + path,
            headers=self.walle.get_headers(),
            verify=self.walle.verify)

        _check_exception(self.logger, self.walle.response)
        return json.loads(self.walle.response.content)


class BlueprintsClient(BaseClient):

    def validate(self, blueprint_path):
        return parser.parse_from_path(blueprint_path)

    def list(self):
        try:
            result = self._get('/blueprints')
            if result:
                return result["items"]
        except WalleException:
            return

    def get(self, blueprint_id):
        try:
            return self._get('/blueprints/%s' % blueprint_id)
        except WalleException:
            return

    def delete(self, blueprint_id):
        try:
            return self._delete('/blueprints/%s' % blueprint_id)
        except WalleException:
            return

    def upload(self, blueprint_path, blueprint_id):
        self.validate(blueprint_path)
        tempdir = tempfile.mkdtemp()
        try:
            tar_path = self._tar_blueprint(blueprint_path, tempdir)
            application_file = os.path.basename(blueprint_path)
            blueprint = self._upload(
                tar_path,
                blueprint_id=blueprint_id,
                application_file_name=application_file)
            return blueprint
        finally:
            shutil.rmtree(tempdir)

    def archive(self, file_name, blueprint_id):
        self.walle.response = requests.get(
            self.walle.url + '/blueprints/%s/archive' % blueprint_id,
            headers=self.walle.get_headers(),
            verify=self.walle.verify)
        _check_exception(self.logger, self.walle.response)
        with open(file_name, "wb") as f:
            f.write(self.walle.response.content)
        return

    @staticmethod
    def _tar_blueprint(blueprint_path, tempdir):
        blueprint_path = expanduser(blueprint_path)
        blueprint_name = os.path.basename(os.path.splitext(blueprint_path)[0])
        blueprint_directory = os.path.dirname(blueprint_path)
        if not blueprint_directory:
            # blueprint path only contains a file name from the local directory
            blueprint_directory = os.getcwd()
        tar_path = os.path.join(tempdir, '{0}.tar.gz'.format(blueprint_name))
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(blueprint_directory,
                    arcname=os.path.basename(blueprint_directory))
        return tar_path

    def _upload(self, tar_file,
                blueprint_id,
                application_file_name=None):
        query_params = {}
        if application_file_name is not None:
            query_params['application_file_name'] = (
                urllib.quote(application_file_name))

        uri = '/blueprints/{0}'.format(blueprint_id)
        url = '{0}{1}'.format(self.walle.url, uri)
        headers = self.walle.get_headers()
        with open(tar_file, 'rb') as f:
            self.walle.response = requests.put(
                url, headers=headers,
                params=query_params,
                data=f, verify=self.walle.verify
            )

        if self.walle.response.status_code not in range(200, 210):
            _check_exception(self.logger, self.walle.response)
        return self.walle.response.json()


class DeploymentsClient(BaseClient):

    def list(self):
        try:
            result = self._get('/deployments')
            if result:
                return result["items"]
        except WalleException:
            return

    def get(self, deployment_id):
        try:
            return self._get('/deployments/%s' % deployment_id)
        except WalleException:
            return

    def delete(self, deployment_id, force_delete=False):
        try:
            return self._delete('/deployments/%s' % deployment_id)
        except WalleException:
            return

    def create(self, blueprint_id, deployment_id, inputs=None):
        data = {
            'blueprint_id': blueprint_id
        }
        if inputs:
            data['inputs'] = inputs
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        try:
            return self._update('/deployments/%s' % deployment_id, data)
        except WalleException:
            return

    def outputs(self, deployment_id):
        try:
            return self._get('/deployments/%s/outputs' % deployment_id)
        except WalleException:
            return


class ExecutionsClient(BaseClient):

    def list(self, deployment_id):
        params = {'deployment_id': deployment_id}
        try:
            result = self._get('/executions', params, False)
            if result:
                return result["items"]
        except WalleException:
            return

    def start(self, deployment_id, workflow_id, parameters=None,
              allow_custom_parameters="false", force="false"):
        data = {
            'deployment_id': deployment_id,
            'workflow_id': workflow_id,
            'parameters': parameters,
            'allow_custom_parameters': allow_custom_parameters,
            'force': force,
        }
        try:
            return self._add('/executions', data)
        except WalleException:
            return

    def cancel(self, execution_id, force="false"):
        data = {
            'force': force
        }
        try:
            return self._add('/executions/' + execution_id, data)
        except WalleException:
            return

    def get(self, execution_id):
        try:
            return self._get('/executions/' + execution_id)
        except WalleException:
            return


class EventsClient(BaseClient):

    def get(self, from_event=0, batch_size=50,
            blueprint=None, deployment=None):
        data = {
            "_offset": from_event,
            "_size": batch_size,
            "blueprint_id": blueprint
        }
        if deployment:
            data["deployment_id"] = deployment
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.get(
            self.walle.url + '/events',
            headers=headers, params=data,
            verify=self.walle.verify)
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)['items']
        except WalleException:
            return


class EndpointsClient(BaseClient):

    def add(self, endpoint_type, endpoint_url, version, description):
        data = {
            'type': endpoint_type,
            'endpoint_url': endpoint_url,
            'version': version,
            'description': description
        }
        return self._add('/endpoints', data)

    def delete(self, endpoint_id):
        return self._delete('/endpoints/%s' % endpoint_id)

    def list(self):
        return self._get('/endpoints')


class TenantsClient(BaseClient):

    def add(self, endpoint_url, endpoint_type, tenant_name,
            cloudify_host, cloudify_port, description, create):
        data = {
            'endpoint_url': endpoint_url,
            'type': endpoint_type,
            'tenant_name': tenant_name,
            'cloudify_host': cloudify_host,
            'cloudify_port': cloudify_port,
            'description': description,
            'create': create
        }
        return self._add('/tenants', data)

    def delete(self, tenants_id, delete_low="false"):
        return self._delete('/tenants/%s?delete=%s' % (
            tenants_id, delete_low
        ))

    def list(self):
        return self._get('/tenants')

    def update(self, tenant_id, endpoint_url, endpoint_type, tenant_name,
               cloudify_host, cloudify_port, description, create):
        data = {
            'id': tenant_id,
            'endpoint_url': endpoint_url,
            'type': endpoint_type,
            'tenant_name': tenant_name,
            'cloudify_host': cloudify_host,
            'cloudify_port': cloudify_port,
            'description': description,
            'create': create
        }
        return self._update('/tenants', data)


class TenantLimitsClient(BaseClient):

    def add(self, endpoint_url, endpoint_type, tenant_name,
            soft, hard, limit_type):
        data = {
            'endpoint_url': endpoint_url,
            'type': endpoint_type,
            'tenant_name': tenant_name,
            'soft': soft,
            'hard': hard,
            'limit_type': limit_type
        }
        return self._add('/limits', data)

    def update(self, limit_id, soft, hard, limit_type):
        data = {
            'id': limit_id,
            'soft': soft,
            'hard': hard,
            'limit_type': limit_type
        }
        return self._update('/limits', data)

    def delete(self, tenants_id):
        return self._delete('/limits/%s' % tenants_id)

    def list(self):
        return self._get('/limits')
