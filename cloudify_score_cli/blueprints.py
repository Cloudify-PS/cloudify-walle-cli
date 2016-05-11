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

import table_format

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
    def short(name, size):
        if len(name) < size:
            return name
        else:
            return name[:size-3] + "..."

    logger.info('Getting blueprints list...')
    format_struct = (
        ("id", 20),
        ("description", 35),
        ("main_file_name", 35),
        ("created_at", 27),
        ("updated_at", 27)
    )
    table_format.print_header(format_struct)
    blueprints = client.blueprints.list()
    if blueprints:
        for blueprint in blueprints:
            table_format.print_row(blueprint, format_struct)


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
