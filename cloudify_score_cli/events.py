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


def proceed_events(client, logger, operation, execution_id, from_event,
                   batch_size, show_logs):
    operations = {'list': _list}
    try:
        operations[operation](client, logger, execution_id, from_event,
                              batch_size, show_logs)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, execution_id, from_event, batch_size, include_logs):
    logger.info('Getting executions list...')
    events = client.events.get(
        execution_id, from_event, batch_size, include_logs
    )
    format_struct = (
        ('timestamp', 30),
        ('event_type', 20),
        ('tags', 10),
        ('node', 30),
        ('text', 60)
    )
    table_format.print_header(format_struct)
    for event in events:
        if isinstance(event, dict):
            table_format.print_row({
                'event_type': event['event_type'],
                'tags': ",".join(event['tags']),
                'timestamp': event['timestamp'],
                'text': event['message']['text'],
                'node': event.get('context', {}).get('node_id')
            }, format_struct)
        else:
            print event
