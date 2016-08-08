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

import table_format

endpoint_format_struct = (
    ("id", 36),
    ("type", 35),
    ("endpoint", 50),
    ("version", 10),
    ("description", 35),
    ("created_at", 27),
)


def proceed_endpoint(client, logger, operation, endpoint_id,
                     endpoint_type, endpoint_url, version, description):
    operations = {'list': _list,
                  'add': _add,
                  'delete': _delete}
    try:
        operations[operation](client, logger, endpoint_id,
                              endpoint_type, endpoint_url, version,
                              description)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting endpoint list...')
    table_format.print_header(endpoint_format_struct)
    endpoints = client.endpoints.list()
    if endpoints:
        for endpoint in endpoints:
            table_format.print_row(endpoint, endpoint_format_struct)


def _add(client, logger, _endpoint_id, endpoint_type, endpoint_url,
         version, description):
    logger.info('Add endpoint...')
    if not endpoint_url or not endpoint_type or not version:
        logger.info('Please check parameters.')
        return
    table_format.print_header(endpoint_format_struct)
    endpoint = client.endpoints.add(endpoint_type, endpoint_url,
                                    version, description)
    table_format.print_row(endpoint, endpoint_format_struct)


def _delete(client, logger, endpoint_id, *args):
    logger.info('Delete endpoint: {0}'.format(endpoint_id))
    if not endpoint_id:
        logger.info("Endpoint name not specified")
        return
    client.endpoints.delete(endpoint_id)
    logger.info('Delete endpoint {0}: done'.format(endpoint_id))
