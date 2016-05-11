import table_format


def proceed_executions(client, logger, operation, deployment_id, workflow_id,
                       parameters):
    operations = {'list': _list,
                  'start': _start,
                  'cancel': _cancel,
                  'get': _get}
    try:
        operations[operation](client, logger, deployment_id, workflow_id, parameters)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, deployment_id, *args):
    logger.info('Getting executions list... for {}'.format(deployment_id))
    format_struct = (
        ('id', 40),
        ('deployment_id', 20),
        ('status', 30),
        ('workflow_id', 30),
        ('created_at', 27)
    )
    table_format.print_header(format_struct)

    executions = client.executions.list(deployment_id)

    if executions:
        for execution in executions:
            table_format.print_row(execution, format_struct)

def _start(client, logger, deployment_id, workflow_id, parameters):
    logger.info('Executions start {0}'.format(deployment_id))
    print client.executions.start(deployment_id, workflow_id, parameters)


def _cancel(client, logger, deployment_id, workflow_id, parameters):
    logger.info('Executions cancel {0}'.format(deployment_id))


def _get(client, logger, workflow_id, deployment, parameters):
    logger.info('Executions get {0}'.format(deployment))
