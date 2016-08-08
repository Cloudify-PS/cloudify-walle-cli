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

limit_format_struct = (
    ("id", 36),
    ('tenant_id', 36),
    ('hard', 5),
    ('soft', 5),
    ('type', 20),
    ("created_at", 27),
    ("updated_at", 27)
)


def proceed_limit(client, logger, operation, limit_id, endpoint_url,
                  endpoint_type, tenant_name, soft, hard, limit_type):
    operations = {'list': _list,
                  'update': _update,
                  'add': _add,
                  'delete': _delete}
    try:
        operations[operation](client, logger, limit_id, endpoint_url,
                              endpoint_type, tenant_name, soft, hard,
                              limit_type)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *arg):
    logger.info('Getting limits list...')
    table_format.print_header(limit_format_struct)
    limits = client.limits.list()
    if limits:
        for limit in limits:
            table_format.print_row(limit, limit_format_struct)


def _add(client, logger, _limit_id, endpoint_url, endpoint_type,
         tenant_name, soft, hard, limit_type):
    logger.info('Add limit...')
    if not endpoint_url or not tenant_name:
        logger.info(
            'Please specify "endpoint_url"/"tenant_name" parameters.'
        )
        return
    table_format.print_header(limit_format_struct)
    limit = client.limits.add(endpoint_url, endpoint_type, tenant_name,
                              soft, hard, limit_type)
    table_format.print_row(limit, limit_format_struct)


def _update(client, logger, limit_id, endpoint_url, endpoint_type,
            tenant_name, soft, hard, limit_type):
    logger.info('Update limit...')
    if not limit_id:
        logger.info(
            'Please specify "limit_id" parameters.'
        )
        return
    table_format.print_header(limit_format_struct)
    limit = client.limits.update(limit_id, soft, hard, limit_type)
    table_format.print_row(limit, limit_format_struct)


def _delete(client, logger, limit_id, endpoint_url, endpoint_type,
            tenant_name, soft, hard, limit_type):
    logger.info('Delete tenant: {0}'.format(limit_id))
    if not limit_id:
        logger.info("Tenant id not specified")
        return
    client.limits.delete(limit_id)
    logger.info('Delete tenant {0}: done'.format(limit_id))
