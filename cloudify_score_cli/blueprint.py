from cloudify_score_cli import get_score_client


def proceed_blueprint(config, logger, operation, blueprint_id, blueprint_file):
    client = get_score_client(config)
    operations ={'list': _list,
                 'info': _info,
                 'validate': _validate,
                 'upload': _upload,
                 'delete': _delete,
                 'status': _status}
    try:
        operations[operation](client, logger, blueprint_id, blueprint_file)
    except KeyError:
        loger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting blueprints list...')
    blueprints =  client.blueprints.list()] 
    pass


def _info(client, logger, blueprint_id, blueprint_file):
    pass


def _validate(client, logger, blueprint_id, blueprint_file):
    logger.info('Validate blueprint {0}'.format(blueprint_id))



def _upload(client, logger, blueprint_id, blueprint_file):
    logger.info('Upload blueprint {0}, file: {1}'.format(blueprint_id, blueprint_file))


def _delete(client, logger, blueprint_id, blueprint_file):
    logger.info('Delete blueprint {0}'.format(blueprint_id))


