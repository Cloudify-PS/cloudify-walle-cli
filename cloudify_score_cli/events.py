def proceed_events(client, logger, operation, execution, from_event,
                   batch_size, show_logs):
    operations = {'list': _list}
    try:
        operations[operation](client, logger, execution, from_event,
                              batch_size, show_logs)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting executions list...')
