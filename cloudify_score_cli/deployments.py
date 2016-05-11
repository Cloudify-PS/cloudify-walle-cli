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

import yaml
import table_format


def proceed_deployments(client, logger, operation, deployment_id, blueprint_id,
                        input_file):
    operations = {'list': _list,
                  'info': _info,
                  'create': _create,
                  'delete': _delete,
                  'output': _output}
    try:
        operations[operation](client, logger, deployment_id, blueprint_id,
                              input_file)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting deployments list...')
    format_struct = (
        ("id", 25),
        ("blueprint_id", 25),
        ("created_at", 27),
        ("updated_at", 27)
    )
    table_format.print_header(format_struct)

    deployments = client.deployments.list()
    if deployments:
        for deployment in deployments:
            table_format.print_row(deployment, format_struct)


def _info(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Deployment info {0}'.format(deployment_id))
    format_struct = (
        ("id", 25),
        ("blueprint_id", 25),
        ("created_at", 27),
        ("updated_at", 27)
    )
    table_format.print_header(format_struct)
    deployment = client.deployments.get(deployment_id)
    table_format.print_row(deployment, format_struct)


def _create(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Create deployments {0}, file: {1}'.format(deployment_id,
                                                           blueprint_id))
    if not deployment_id or not blueprint_id:
        logger.info('Please check parameters.')
        return
    inputs = None
    if input_file:
        inputs = yaml.load(input_file)
    client.deployments.create(blueprint_id, deployment_id, inputs)
    logger.info('Create deployments {0}: done'.format(deployment_id))


def _delete(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Delete deployment {0}'.format(deployment_id))
    print client.deployments.delete(deployment_id)


def _output(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Output for deployment {0}'.format(deployment_id))
    print client.deployments.outputs(deployment_id)
