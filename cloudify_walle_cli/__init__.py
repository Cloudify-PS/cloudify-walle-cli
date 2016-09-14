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
import walle
import json

_logger = None

CONFIGFILE = '.walle'
WALLE_SECTION = 'Walle'


USER = 'user'
PASSWORD = 'password'
HOST = 'host'
TENANT = 'tenant'
TOKEN = 'token'
REGION = 'region'
WALLE_HOST = 'walle_host'
WALLE_VERIFY = 'verify'
HEADERS = 'headers'

DEFAULT_PROTOCOL = 'http'
SECURED_PROTOCOL = 'https'


Configuration = collections.namedtuple('Configuration',
                                       'walle_host, verify, headers')


def get_logger():
    global _logger
    if _logger is not None:
        return _logger
    log_format = ('%(filename)s[LINE:%(lineno)d]# %(levelname)-8s'
                  ' [%(asctime)s]  %(message)s')
    _logger = logging.getLogger("walle_cli_logger")
    _logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def save_openstack_config(openstack):
    config = ConfigParser.RawConfigParser()
    config.add_section(WALLE_SECTION)
    config.set(WALLE_SECTION, WALLE_HOST, openstack.walle_host)
    config.set(WALLE_SECTION, WALLE_VERIFY, openstack.verify)
    headers = {}
    headers["x-openstack-authorization"] = openstack.token
    headers["x-openstack-keystore-url"] = openstack.host
    headers["x-openstack-keystore-region"] = openstack.region
    headers["x-openstack-keystore-tenant"] = openstack.tenant
    config.set(WALLE_SECTION, HEADERS, json.dumps(headers))

    with open(CONFIGFILE, 'wb') as configfile:
        config.write(configfile)


def load_config(logger):
    try:
        walleconfig = Configuration
        config = ConfigParser.ConfigParser()
        config.read(CONFIGFILE)
        walleconfig.walle_host = config.get(WALLE_SECTION, WALLE_HOST, None)
        walleconfig.verify = config.get(WALLE_SECTION, WALLE_VERIFY, True)
        walleconfig.headers = json.loads(config.get(WALLE_SECTION, HEADERS, {}))
        return walleconfig
    except ConfigParser.NoSectionError:
        raise RuntimeError("Can't load config. Please use 'login' command")


def get_walle_client(config, logger):
    return walle.Walle(
        config.walle_host, headers=config.headers, verify=config.verify,
        logger=logger)
