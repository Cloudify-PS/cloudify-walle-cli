def proceed_blueprint(client, logger, operation, blueprint_id, blueprint_file):
    operations = {'list': _list,
                  'validate': _validate,
                  'upload': _upload,
                  'delete': _delete}
    try:
        operations[operation](client, logger, blueprint_id, blueprint_file)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting blueprints list...')
    blueprints = client.blueprints.list()
    print blueprints


def _validate(client, logger, blueprint_id, blueprint_file):
    logger.info('Validate blueprint {0}'.format(blueprint_id))


def _upload(client, logger, blueprint_id, blueprint_file):
    logger.info('Upload blueprint {0}, file: {1}'.format(blueprint_id,
                                                         blueprint_file))


def _delete(client, logger, blueprint_id, blueprint_file):
    logger.info('Delete blueprint {0}'.format(blueprint_id))
