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

import logging
import ConfigParser
import collections
import score

_logger = None

CONFIGFILE = '.score'
SECTION = 'Openstack'

USER = 'user'
PASSWORD = 'password'
HOST = 'host'
TENANT = 'tenant'
TOKEN = 'token'
REGION = 'region'
SCORE_HOST = 'score_host'

DEFAULT_PROTOCOL = 'http'
SECURED_PROTOCOL = 'https'


Configuration = collections.namedtuple('Configuration',
                                       'user, password, '
                                       'host, tenant, project, '
                                       'region, token, score_host')


def get_logger():
    global _logger
    if _logger is not None:
        return _logger
    log_format = ('%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]'
                  '  %(message)s')
    _logger = logging.getLogger("score_cli_logger")
    _logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def save_config(service_parameters):
    _save_openstack_config(service_parameters)


def load_config(logger):
    return _load_openstack_config(logger)


def _save_openstack_config(openstack):
    config = ConfigParser.RawConfigParser()
    config.add_section(SECTION)
    config.set(SECTION, USER, openstack.user)
    config.set(SECTION, PASSWORD, openstack.password)
    config.set(SECTION, HOST, openstack.host)
    config.set(SECTION, TENANT, openstack.tenant)
    config.set(SECTION, REGION, openstack.region)
    config.set(SECTION, TOKEN, openstack.token)
    config.set(SECTION, SCORE_HOST, openstack.score_host)

    with open(CONFIGFILE, 'wb') as configfile:
        config.write(configfile)


def _load_openstack_config(logger):
    openstack = Configuration
    try:
        config = ConfigParser.ConfigParser()
        config.read(CONFIGFILE)
        openstack.user = config.get(SECTION, USER, None)
        openstack.password = config.get(SECTION, PASSWORD, None)
        openstack.host = config.get(SECTION, HOST, None)
        openstack.tenant = config.get(SECTION, TENANT, None)
        openstack.region = config.get(SECTION, REGION, None)
        openstack.token = config.get(SECTION, TOKEN, None)
        openstack.score_host = config.get(SECTION, SCORE_HOST, None)
    except ConfigParser.NoSectionError as e:
        logger.info(e)
        raise RuntimeError("Can't load config. Please use 'login' command")
    return openstack


def get_score_client(config, logger):
    return score.Score(
        config.score_host, auth_url=config.host, token=config.token,
        region=config.region, verify=True, logger=logger
    )
