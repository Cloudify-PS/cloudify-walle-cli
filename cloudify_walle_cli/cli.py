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

import click
from cloudify_walle_cli import (get_logger, load_config, save_config,
                                Configuration)
from login import login_to_openstack
from cloudify_walle_cli import get_walle_client
from blueprints import proceed_blueprint
from deployments import proceed_deployments
from executions import proceed_executions
from events import proceed_events
from endpoints import proceed_endpoint
from tenants import proceed_tenant
from limits import proceed_limit

default_operation = 'list'
LOGGER = 'logger'
CONFIG = 'config'
CLIENT = 'client'


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug
    ctx.obj[LOGGER].debug('cli')


@cli.command()
@click.pass_context
@click.argument('user')
@click.option('-p', '--password', metavar='<password>', help='Password')
@click.option('-h', '--host', metavar='<host>', help='Openstack host')
@click.option('-t', '--tenant', metavar='<tenant-name>', help='Tenant name')
@click.option('-r', '--region', metavar='<region-name>', help='Region name')
@click.option('-s', '--walle-host', 'walle_host',
              metavar='<walle>', help='URL of the Walle server')
@click.option('-v', '--verify', metavar='<verify>',
              help='Verify connection', default=True)
def login(ctx, user, password, host, tenant, region, walle_host, verify):
    logger = ctx.obj[LOGGER]
    logger.debug('login')
    verify = ("true" == str(verify).lower())
    token = login_to_openstack(logger, user, password, host, tenant,
                               walle_host, verify)
    if not token:
        print "Wrong credentials"
    openstack = Configuration
    openstack.user = user
    openstack.password = password
    openstack.host = host
    openstack.token = token
    openstack.walle_host = walle_host
    openstack.region = region
    openstack.tenant = tenant
    openstack.verify = verify
    save_config(openstack)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list |  validate | upload | delete | archive]',
                type=click.Choice(['list',  'validate', 'upload',
                                   'delete', 'archive']))
@click.option('-b', '--blueprint', 'blueprint_id', default='',
              metavar='<blueprint-id>',
              help='Name of the blueprint to create')
@click.option('-f', '--file', 'blueprint_file',
              default=None, metavar='<blueprint-file>',
              help='Local file name of the blueprint to upload',
              type=click.Path(exists=True))
@click.option('-a', '--archive', 'blueprint_archive_file',
              default=None, metavar='<blueprint-archive-file>',
              help='File name for the archove of blueprint')
def blueprints(ctx, operation, blueprint_id, blueprint_file,
               blueprint_archive_file):
    logger = ctx.obj[LOGGER]
    logger.debug('blueprint')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_blueprint(
        client, logger, operation, blueprint_id, blueprint_file,
        blueprint_archive_file)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list | info | create | delete | output]',
                type=click.Choice(['list', 'info', 'create', 'delete',
                                   'output']))
@click.option('-d', '--deployment', 'deployment_id', default='',
              metavar='<deployment-id>', help='Deployment Id')
@click.option('-b', '--blueprint', 'blueprint_id', default=None,
              metavar='<blueprint-id>', help='Blueprint Id')
@click.option('-i', '--inputs', 'input_file', default=None,
              metavar='<input-file>',
              help='Local file with the input values '
                   'for the deployment (YAML)',
              type=click.File('r'))
@click.option('-f', '--force', default=False,
              metavar='<force>', help='Force operation')
def deployments(ctx, operation, deployment_id, blueprint_id,
                input_file, force):
    logger = ctx.obj[LOGGER]
    logger.debug('deployment')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_deployments(
        client, logger, operation, deployment_id, blueprint_id,
        input_file, force
    )


@cli.command()
@click.argument('operation', default=default_operation,
                metavar='[list | start | cancel | get]',
                type=click.Choice(['list', 'start', 'cancel', 'get']))
@click.option('-w', '--workflow', default=None,
              metavar='<workflow-id>', help='Workflow Id')
@click.option('-d', '--deployment', 'deployment_id', default='',
              metavar='<deployment-id>', help='Deployment Id')
@click.option('-p', '--parameters', default=None,
              metavar='<parameters>', help='Execution parameters')
@click.option('-e', '--execution', "execution_id", metavar='<execution-id>',
              help='Execution Id')
@click.option('-f', '--force', default="false",
              metavar='<force>', help='Force operation')
@click.pass_context
def executions(
    ctx, operation, workflow, deployment_id, parameters, execution_id, force
):
    logger = ctx.obj[LOGGER]
    logger.debug('executions')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_executions(client, logger, operation, deployment_id, workflow,
                       parameters, execution_id, force)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list]',
                type=click.Choice(['list']))
@click.option('-f', '--from', 'from_event',
              default=0, metavar='<from_event>',
              help='From event')
@click.option('-s', '--size', 'batch_size',
              default=100, metavar='<batch_size>',
              help='Size batch of events')
@click.option('-d', '--deployment', 'deployment_id', default=None,
              metavar='<deployment-id>', help='Deployment Id')
@click.option('-b', '--blueprint', 'blueprint_id', default=None,
              metavar='<blueprint-id>', help='Blueprint Id')
def events(ctx, operation, from_event,
           batch_size, blueprint_id, deployment_id):
    logger = ctx.obj[LOGGER]
    logger.debug('event')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_events(client, logger, operation, from_event,
                   batch_size, blueprint_id, deployment_id)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list, add, delete]',
                type=click.Choice(['list', 'add', 'delete']))
@click.option('-e', '--endpoint-id', default='',
              metavar='<endpoint-id>', help='Endpoint Id')
@click.option('-t', '--endpoint-type', default='openstack',
              metavar='<endpoint-type>', help='Endpoint type')
@click.option('-u', '--endpoint-url', default='',
              metavar='<endpoint-url>', help='Endpoint url')
@click.option('-v', '--version', default='',
              metavar='<version>', help='Endpoint version')
@click.option('-d', '--description', default='',
              metavar='<description>', help='Endpoint description')
def endpoints(ctx, operation, endpoint_id, endpoint_type, endpoint_url,
              version, description):
    logger = ctx.obj[LOGGER]
    logger.debug('endpoints')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_endpoint(client, logger, operation, endpoint_id,
                     endpoint_type, endpoint_url, version, description)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list, add, delete, update]',
                type=click.Choice(['list', 'add', 'delete', 'update']))
@click.option('-i', '--tenant-id', default='',
              metavar='<tenant-id>', help='Tenant Id')
@click.option('-u', '--endpoint-url', default='',
              metavar='<endpoint-url>', help='Endpoint url')
@click.option('-t', '--endpoint-type', default='openstack',
              metavar='<endpoint-type>', help='Endpoint type')
@click.option('-n', '--tenant-name', default='',
              metavar='<tenant-name>', help='Tenant name')
@click.option('-c', '--cloudify-host', default='',
              metavar='<cloudify-host>', help='Cloudify host')
@click.option('-p', '--cloudify-port', default='',
              metavar='<cloudify-port>', help='Cloudify port')
@click.option('-d', '--description', default='',
              metavar='<description>', help='Tenant description')
@click.option('-r', '--create', default='',
              metavar='<create>', help='Create tenant on low level')
def tenants(ctx, operation, tenant_id, endpoint_url, endpoint_type,
            tenant_name, cloudify_host, cloudify_port, description,
            create):
    logger = ctx.obj[LOGGER]
    logger.debug('tenants')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_tenant(client, logger, operation, tenant_id, endpoint_url,
                   endpoint_type, tenant_name, cloudify_host,
                   cloudify_port, description, create)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list, add, delete, update]',
                type=click.Choice(['list', 'add', 'delete', 'update']))
@click.option('-i', '--limit-id', default='',
              metavar='<limit-id>', help='Limit Id')
@click.option('-u', '--endpoint-url', default='',
              metavar='<endpoint-url>', help='Endpoint url')
@click.option('-t', '--endpoint-type', default='openstack',
              metavar='<endpoint-type>', help='Endpoint type')
@click.option('-n', '--tenant-name', default='',
              metavar='<tenant-name>', help='Tenant name')
@click.option('-s', '--soft', default='',
              metavar='<soft>', help='Soft limit')
@click.option('-d', '--hard', default='',
              metavar='<hard>', help='Hard limit')
@click.option('-l', '--limit-type', default='',
              metavar='<limit-type>', help='Limit type')
def limits(ctx, operation, limit_id, endpoint_url, endpoint_type,
           tenant_name, soft, hard, limit_type):
    logger = ctx.obj[LOGGER]
    logger.debug('limits')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    proceed_limit(client, logger, operation, limit_id, endpoint_url,
                  endpoint_type, tenant_name, soft, hard, limit_type)


@cli.command()
@click.pass_context
def status(ctx):
    logger = ctx.obj[LOGGER]
    ctx.obj[LOGGER].debug('status')
    config = load_config(logger)
    client = _get_walle_client(config, logger)
    if not client:
        return
    status_result = client.get_status()
    print status_result


def _get_walle_client(config, logger):
    if not config:
        click.echo('Empty config')
        return None
    return get_walle_client(config, logger)


def main():
    logger = get_logger()
    cli(obj={LOGGER: logger})


if __name__ == '__main__':
    main()
