def proceed_executions(client, logger, operation, workflow,
                       deployment, parameters):
    operations = {'list': _list,
                  'start': _start,
                  'cancel': _cancel,
                  'get': _get}
    try:
        operations[operation](client, logger, workflow, deployment, parameters)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting executions list...')


def _start(client, logger, workflow, deployment, parameters):
    logger.info('Executions start {0}'.format(deployment))


def _cancel(client, logger, workflow, deployment, parameters):
    logger.info('Executions cancel {0}'.format(deployment))


def _get(client, logger, workflow, deployment, parameters):
    logger.info('Executions get {0}'.format(deployment))
