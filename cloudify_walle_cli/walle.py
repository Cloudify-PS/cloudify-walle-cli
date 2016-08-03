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


class BlueprintsClient(object):

    def __init__(self, walle, logger=None):
        self.walle = walle
        self.logger = logger

    def validate(self, blueprint_path):
        return parser.parse_from_path(blueprint_path)

    def list(self):
        self.walle.response = requests.get(self.walle.url + '/blueprints',
                                           headers=self.walle.get_headers(),
                                           verify=self.walle.verify)
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)["items"]
        except WalleException:
            return

    def get(self, blueprint_id):
        self.walle.response = requests.get(
            self.walle.url + '/blueprints/%s' % blueprint_id,
            headers=self.walle.get_headers(),
            verify=self.walle.verify)
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return

    def delete(self, blueprint_id):
        self.walle.response = requests.delete(
            self.walle.url + '/blueprints/%s' % blueprint_id,
            headers=self.walle.get_headers(),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
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


class DeploymentsClient(object):

    def __init__(self, walle, logger=False):
        self.walle = walle
        self.logger = logger

    def list(self):
        self.walle.response = requests.get(
            self.walle.url + '/deployments',
            headers=self.walle.get_headers(),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)["items"]
        except WalleException:
            return

    def get(self, deployment_id):
        self.walle.response = requests.get(
            self.walle.url + '/deployments/%s' % deployment_id,
            headers=self.walle.get_headers(),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return

    def delete(self, deployment_id, force_delete=False):

        self.walle.response = requests.delete(
            self.walle.url + '/deployments/%s' % deployment_id,
            params={"ignore_live_nodes": force_delete},
            headers=self.walle.get_headers(),
            verify=self.walle.verify)

        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
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
        self.walle.response = requests.put(
            self.walle.url + '/deployments/%s' % deployment_id,
            data=json.dumps(data),
            headers=headers,
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return

    def outputs(self, deployment_id):
        headers = self.walle.get_headers()
        self.walle.response = requests.get(
            self.walle.url + '/deployments/%s/outputs' % deployment_id,
            headers=headers,
            verify=self.walle.verify
        )

        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return


class ExecutionsClient(object):

    def __init__(self, walle, logger=False):
        self.walle = walle
        self.logger = logger

    def list(self, deployment_id):
        params = {'deployment_id': deployment_id}
        self.walle.response = requests.get(
            self.walle.url + '/executions',
            headers=self.walle.get_headers(),
            params=params, verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)["items"]
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
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.post(
            self.walle.url + '/executions',
            headers=headers,
            data=json.dumps(data),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return

    def cancel(self, execution_id, force="false"):
        data = {
            'force': force
        }
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.post(
            self.walle.url + '/executions/' + execution_id,
            headers=headers, data=json.dumps(data),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return

    def get(self, execution_id):
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.get(
            self.walle.url + '/executions/' + execution_id,
            headers=headers,
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return


class EventsClient(object):

    def __init__(self, walle, logger=False):
        self.walle = walle
        self.logger = logger

    def get(self, execution_id, from_event=0, batch_size=100,
            include_logs=False):
        data = {
            "execution_id": execution_id,
            "from": from_event,
            "size": batch_size,
            "include_logs": include_logs
        }
        headers = self.walle.get_headers()
        headers['Content-type'] = 'application/json'
        self.walle.response = requests.get(
            self.walle.url + '/events',
            headers=headers, data=json.dumps(data),
            verify=self.walle.verify
        )
        try:
            _check_exception(self.logger, self.walle.response)
            return json.loads(self.walle.response.content)
        except WalleException:
            return
