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
import pprint
import table_format


def proceed_deployments(client, logger, operation, deployment_id, blueprint_id,
                        input_file, force):
    operations = {'list': _list,
                  'info': _info,
                  'create': _create,
                  'delete': _delete,
                  'output': _output}
    try:
        operations[operation](client, logger, deployment_id, blueprint_id,
                              input_file, force)
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

    deployments = client.deployments.list()
    if deployments:
        table_format.print_header(format_struct)
        for deployment in deployments:
            table_format.print_row(deployment, format_struct)


def _info(client, logger, deployment_id, *args):
    logger.info('Deployment info {0}'.format(deployment_id))
    if not deployment_id:
        logger.info("Deployment name not specified. Use -d key")
        return
    format_struct = (
        ("id", 25),
        ("blueprint_id", 25),
        ("created_at", 27),
        ("updated_at", 27)
    )
    deployment = client.deployments.get(deployment_id)
    if deployment:
        table_format.print_header(format_struct)
        table_format.print_row(deployment, format_struct)


def _create(client, logger, deployment_id, blueprint_id, input_file, force):
    if not deployment_id or not blueprint_id:
        logger.info('Please check parameters: -d for depolyment, '
                    '-b for blueprint, -i for inputs')
        return
    logger.info('Create deployment {0}, for blueprint: {1}'
                .format(deployment_id,
                        blueprint_id))
    inputs = None
    if input_file:
        inputs = yaml.load(input_file)
    client.deployments.create(blueprint_id, deployment_id, inputs)
    logger.info('Create deployments {0}: done'.format(deployment_id))


def _delete(client, logger, deployment_id, blueprint_id, input_file, force):
    logger.info('Delete deployment {0}'.format(deployment_id))
    if not deployment_id:
        logger.info("Deployment name not specified")
        return
    if force:
        logger.info("Delete with force flag.")
    deployment = client.deployments.delete(deployment_id, force)
    if deployment:
        logger.info('Delete deployments {0}: done'.format(deployment_id))


def _output(client, logger, deployment_id, *args):
    logger.info('Output for deployment {0}'.format(deployment_id))
    deployment = client.deployments.outputs(deployment_id)
    if deployment:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(deployment['outputs'])
