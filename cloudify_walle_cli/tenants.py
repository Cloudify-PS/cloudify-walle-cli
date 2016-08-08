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

tenant_format_struct = (
    ("id", 36),
    ("tenant_name", 20),
    ("endpoint_id", 36),
    ("type", 10),
    ("endpoint", 50),
    ("cloudify_host", 25),
    ("cloudify_port", 5),
    ("description", 10),
    ("created_at", 27),
    ("updated_at", 27)
)


def proceed_tenant(client, logger, operation, tenant_id, endpoint_url,
                   endpoint_type, tenant_name, cloudify_host,
                   cloudify_port, description, create):
    operations = {'list': _list,
                  'add': _add,
                  'delete': _delete,
                  'update': _update}
    try:
        operations[operation](client, logger, tenant_id, endpoint_url,
                              endpoint_type, tenant_name, cloudify_host,
                              cloudify_port, description, create)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *arg):
    logger.info('Getting tenants list...')
    table_format.print_header(tenant_format_struct)
    tenants = client.tenants.list()
    if tenants:
        for tenant in tenants:
            table_format.print_row(tenant, tenant_format_struct)


def _add(client, logger, _tenant_id, endpoint_url, endpoint_type,
         tenant_name, cloudify_host, cloudify_port, description, create):
    logger.info('Add tenant...')
    if not endpoint_url or not tenant_name:
        logger.info(
            'Please specify "endpoint_url"/"tenant_name" parameters.'
        )
        return
    table_format.print_header(tenant_format_struct)
    tenant = client.tenants.add(endpoint_url, endpoint_type, tenant_name,
                                cloudify_host, cloudify_port,
                                description, create)
    table_format.print_row(tenant, tenant_format_struct)


def _delete(client, logger, tenant_id, endpoint_url, endpoint_type,
            tenant_name, cloudify_host, cloudify_port, description,
            create):
    logger.info('Delete tenant: {0}'.format(tenant_id))
    if not tenant_id:
        logger.info("Tenant id not specified")
        return
    client.tenants.delete(tenant_id, create)
    logger.info('Delete tenant {0}: done'.format(tenant_id))


def _update(client, logger, tenant_id, endpoint_url, endpoint_type,
            tenant_name, cloudify_host, cloudify_port, description, create):
    logger.info('Update tenant: {0}'.format(tenant_id))
    if not tenant_id:
        logger.info("Tenant id not specified")
        return
    tenant = client.tenants.update(
        tenant_id, endpoint_url, endpoint_type, tenant_name,
        cloudify_host, cloudify_port, description, create
    )
    table_format.print_row(tenant, tenant_format_struct)
