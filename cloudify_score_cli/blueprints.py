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
    print client.blueprints.validate(blueprint_file)


def _upload(client, logger, blueprint_id, blueprint_file):
    logger.info('Upload blueprint {0}, file: {1}'.format(blueprint_id,
                                                         blueprint_file))
    if not blueprint_id or not blueprint_file:
        logger.info('Please check parameters.')
        return
    client.blueprints.upload(blueprint_file, blueprint_id)
    logger.info('Upload blueprint {0}: done'.format(blueprint_id))


def _delete(client, logger, blueprint_id, blueprint_file):
    logger.info('Delete blueprint {0}'.format(blueprint_id))
    client.blueprints.delete(blueprint_id)
    logger.info('Delete blueprint {0}: done'.format(blueprint_id))
