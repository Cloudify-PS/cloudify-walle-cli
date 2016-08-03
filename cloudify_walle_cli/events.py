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

import pprint


def proceed_events(client, logger, operation, from_event,
                   batch_size, blueprint, deployment):
    operations = {'list': _list}
    try:
        operations[operation](client, logger, from_event,
                              batch_size, blueprint, deployment)
    except KeyError:
        logger.error('Unknown operation')


def _list(client, logger, from_event,
          batch_size, blueprint, deployment):
    logger.info('Getting events list...')
    if not blueprint:
        logger.info('Please specify blueprint with key -b.')
        return
    events = client.events.get(from_event,
                               batch_size, blueprint, deployment)
    pp = pprint.PrettyPrinter(indent=2)
    for event in events:
        pp.pprint(event)
