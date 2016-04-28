import click
from cloudify_score_cli import get_logger


default_operation = 'list'
LOGGER = 'LOGGER'


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj[LOGGER].debug('cli') 
    ctx.obj['DEBUG'] = debug


@cli.command()
@click.pass_context
@click.argument('user')
@click.option('-p', '--password', metavar='<password>', help='Password')
@click.option('-h', '--host', metavar='<host>', help='Openstack host')
@click.option('-s', '--score-host', 'score_host',
              metavar='<score>', help='URL of the Score server')
def login(ctx, user, password, host, score_host):
    ctx.obj[LOGGER].debug('login')    


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list | info | validate | upload | delete | status]',
                type=click.Choice(['list', 'info', 'validate', 'upload',
                                   'delete', 'status']))
@click.option('-b', '--blueprint', 'blueprint_id', default='',
              metavar='<blueprint-id>',
              help='Name of the blueprint to create')
@click.option('-f', '--file', 'blueprint_file',
              default=None, metavar='<blueprint-file>',
              help='Local file name of the blueprint to upload',
              type=click.Path(exists=True))                
def blueprint(ctx, operation, blueprint_id, blueprint_file):
    ctx.obj[LOGGER].debug('blueprint')


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list | info | create | delete | execute | cancel '
                        '| output]',
                type=click.Choice(['list', 'info', 'create', 'delete',
                                   'execute', 'cancel', 'output'
                                   ]))
@click.option('-w', '--workflow', default=None,
              metavar='<workflow-id>', help='Workflow Id')
@click.option('-d', '--deployment', 'deployment_id', default='',
              metavar='<deployment-id>', help='Deployment Id')
@click.option('-b', '--blueprint', 'blueprint_id', default=None,
              metavar='<blueprint-id>', help='Blueprint Id')
@click.option('-f', '--file', 'input_file', default=None,
              metavar='<input-file>',
              help='Local file with the input values '
                   'for the deployment (YAML)',
              type=click.File('r'))
@click.option('-s', '--show-events', 'show_events',
              is_flag=True, default=False, help='Show events')
@click.option('-e', '--execution', default=None,
              metavar='<execution-id>', help='Execution Id')
def deployment(ctx, operation, deployment_id, blueprint_id,
               input_file, workflow, show_events, execution):
    ctx.obj[LOGGER].debug('deployment')


@cli.command()
@click.pass_context
@click.argument('operation', default=default_operation,
                metavar='[list]',
                type=click.Choice(['list']))
@click.option('-i', '--id', 'execution', metavar='<execution-id>',
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
def event(ctx, operation, execution, from_event, batch_size, show_logs):
    ctx.obj[LOGGER].debug('event')    


if __name__ == '__main__':
    logger = get_logger()
    cli(obj={LOGGER:logger})

