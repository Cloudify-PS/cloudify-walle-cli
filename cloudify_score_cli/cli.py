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
from cloudify_score_cli import (get_logger, load_config, save_config,
                                Configuration)
from login import login_to_openstack
from cloudify_score_cli import get_score_client
from blueprints import proceed_blueprint
from deployments import proceed_deployments
from executions import proceed_executions
from events import proceed_events

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
@click.option('-s', '--score-host', 'score_host',
              metavar='<score>', help='URL of the Score server')
def login(ctx, user, password, host, tenant, score_host):
    logger = ctx.obj[LOGGER]
    logger.debug('login')
    token = login_to_openstack(logger, user, password, host, tenant, score_host)
    if not token:
        print "Wrong credentials"
    openstack = Configuration
    openstack.user = user
    openstack.password = password
    openstack.host = host
    openstack.token = token
    openstack.score_host = score_host
    openstack.tenant = tenant
    save_config(openstack)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list |  validate | upload | delete ]',
                type=click.Choice(['list',  'validate', 'upload',
                                   'delete']))
@click.option('-b', '--blueprint', 'blueprint_id', default='',
              metavar='<blueprint-id>',
              help='Name of the blueprint to create')
@click.option('-f', '--file', 'blueprint_file',
              default=None, metavar='<blueprint-file>',
              help='Local file name of the blueprint to upload',
              type=click.Path(exists=True))
def blueprints(ctx, operation, blueprint_id, blueprint_file):
    logger = ctx.obj[LOGGER]
    logger.debug('blueprint')
    config = load_config(logger)
    client = _get_score_client(config, logger)
    if not client:
        return
    proceed_blueprint(
        client, logger, operation, blueprint_id, blueprint_file
    )


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
def deployments(ctx, operation, deployment_id, blueprint_id,
                input_file):
    logger = ctx.obj[LOGGER]
    logger.debug('deployment')
    config = load_config(logger)
    client = _get_score_client(config, logger)
    if not client:
        return
    proceed_deployments(
        client, logger, operation, deployment_id, blueprint_id,
        input_file
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
@click.pass_context
def executions(ctx, operation, workflow, deployment_id, parameters):
    logger = ctx.obj[LOGGER]
    logger.debug('executions')
    config = load_config(logger)
    client = _get_score_client(config, logger)
    if not client:
        return
    proceed_executions(client, logger, operation, deployment_id, workflow,
                       parameters)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list]',
                type=click.Choice(['list']))
@click.option('-e', '--execution', "execution_id", metavar='<execution-id>',
              required=True, help='Execution Id')
@click.option('-f', '--from', 'from_event',
              default=0, metavar='<from_event>',
              help='From event')
@click.option('-s', '--size', 'batch_size',
              default=100, metavar='<batch_size>',
              help='Size batch of events')
@click.option('-l', '--show-logs', 'show_logs',
              is_flag=True, default=False,
              help='Show logs for event')
def events(ctx, operation, execution_id, from_event, batch_size, show_logs):
    logger = ctx.obj[LOGGER]
    logger.debug('event')
    config = load_config(logger)
    client = _get_score_client(config, logger)
    if not client:
        return
    proceed_events(client, logger, operation, execution_id, from_event,
                   batch_size, show_logs)


@cli.command()
@click.pass_context
def status(ctx):
    logger = ctx.obj[LOGGER]
    ctx.obj[LOGGER].debug('status')
    config = load_config(logger)
    client = _get_score_client(config, logger)
    if not client:
        return
    status_result = client.get_status()
    print status_result


def _get_score_client(config, logger):
    if not config:
        click.echo('Empty config')
        return None
    return get_score_client(config, logger)


def main():
    logger = get_logger()
    cli(obj={LOGGER: logger})


if __name__ == '__main__':
    main()
