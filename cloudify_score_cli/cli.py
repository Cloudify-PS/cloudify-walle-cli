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
@click.option('-n', '--project', metavar='<project-name>', help='Project name')
@click.option('-r', '--region', metavar='<region-name>', help='Region name')
@click.option('-s', '--score-host', 'score_host',
              metavar='<score>', help='URL of the Score server')
def login(ctx, user, password, host, tenant, project, region, score_host):
    ctx.obj[LOGGER].debug('login')
    token = login_to_openstack(user, password, host)
    openstack = Configuration
    openstack.user = user
    openstack.password = password
    openstack.host = host
    openstack.token = token
    openstack.score_host = score_host
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
    ctx.obj[LOGGER].debug('blueprint')
    client = _get_score_client(ctx.obj[CONFIG])
    if not client:
        return
    proceed_blueprint(client, logger, operation, blueprint_id, blueprint_file)


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
    ctx.obj[LOGGER].debug('deployment')
    client = _get_score_client(ctx.obj[CONFIG])
    if not client:
        return
    proceed_deployments(client, logger, operation, deployment_id, blueprint_id,
                        input_file)


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
def executions(ctx, operation, workflow, deployment, parameters):
    ctx.obj[LOGGER].debug('executions')
    client = _get_score_client(ctx.obj[CONFIG])
    if not client:
        return
    proceed_executions(client, logger, operation, workflow,
                       deployment, parameters)


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list]',
                type=click.Choice(['list']))
@click.option('-e', '--execution' 'execution', metavar='<execution-id>',
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
def events(ctx, operation, execution, from_event, batch_size, show_logs):
    ctx.obj[LOGGER].debug('event')
    client = _get_score_client(ctx.obj[CONFIG])
    if not client:
        return
    proceed_events(client, logger, operation, execution, from_event,
                   batch_size, show_logs)


@cli.command()
@click.pass_context
def status(ctx):
    ctx.obj[LOGGER].debug('status')
    client = _get_score_client(ctx.obj[CONFIG])
    if not client:
        return
    status_result = client.manager.get_status()
    print status_result


def _get_score_client(config):
    if not config:
        click.echo('Empty config')
        return None
    return get_score_client(config)


if __name__ == '__main__':
    logger = get_logger()
    config = load_config(logger)
    cli(obj={LOGGER: logger, CONFIG: config})
