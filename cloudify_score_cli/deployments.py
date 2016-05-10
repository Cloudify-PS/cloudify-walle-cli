import yaml


def proceed_deployments(client, logger, operation, deployment_id, blueprint_id,
                        input_file):
    operations = {'list': _list,
                  'info': _info,
                  'create': _create,
                  'delete': _delete,
                  'output': _output}
    try:
        operations[operation](client, logger, deployment_id, blueprint_id,
                              input_file)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, *args):
    logger.info('Getting deployments list...')
    deployments = client.deployments.list()
    print deployments


def _info(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Deployment info {0}'.format(deployment_id))
    print client.deployments.get(deployment_id)


def _create(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Create deployments {0}, file: {1}'.format(deployment_id,
                                                           blueprint_id))
    if not deployment_id or not blueprint_id:
        logger.info('Please check parameters.')
        return
    inputs = None
    if input_file:
        inputs = yaml.load(input_file)
    client.deployments.create(blueprint_id, deployment_id, inputs)
    logger.info('Create deployments {0}: done'.format(deployment_id))


def _delete(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Delete deployment {0}'.format(deployment_id))
    print client.deployments.delete(deployment_id)


def _output(client, logger, deployment_id, blueprint_id, input_file):
    logger.info('Output for deployment {0}'.format(deployment_id))
    print client.deployments.outputs(deployment_id)
