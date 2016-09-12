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
OPENSTACK_SECTION = 'Openstack'
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
                                       'user, password, '
                                       'host, tenant, '
                                       'region, headers, walle_host, verify')


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
    config.add_section(OPENSTACK_SECTION)
    config.set(OPENSTACK_SECTION, USER, openstack.user)
    config.set(OPENSTACK_SECTION, PASSWORD, openstack.password)
    config.set(OPENSTACK_SECTION, HOST, openstack.host)
    config.set(OPENSTACK_SECTION, TENANT, openstack.tenant)
    config.set(OPENSTACK_SECTION, REGION, openstack.region)
    config.set(OPENSTACK_SECTION, WALLE_HOST, openstack.walle_host)
    config.set(OPENSTACK_SECTION, WALLE_VERIFY, openstack.verify)
    headers = {}
    headers["x-openstack-authorization"] = openstack.token
    headers["x-openstack-keystore-url"] = openstack.host
    headers["x-openstack-keystore-region"] = openstack.region
    headers["x-openstack-keystore-tenant"] = openstack.tenant
    config.set(OPENSTACK_SECTION, HEADERS, json.dumps(headers))

    with open(CONFIGFILE, 'wb') as configfile:
        config.write(configfile)


def save_walle_config(walleconfig):
    config = ConfigParser.RawConfigParser()
    config.add_section(WALLE_SECTION)
    config.set(WALLE_SECTION, USER, walleconfig.user)
    config.set(WALLE_SECTION, PASSWORD, walleconfig.password)
    config.set(WALLE_SECTION, WALLE_HOST, walleconfig.walle_host)
    config.set(WALLE_SECTION, WALLE_VERIFY, walleconfig.verify)
    headers = {}
    headers["x-walle-authorization"] = walleconfig.token
    config.set(WALLE_SECTION, HEADERS, json.dumps(headers))
    with open(CONFIGFILE, 'wb') as configfile:
        config.write(configfile)


def load_config(logger):
    try:
        openstack = Configuration
        config = ConfigParser.ConfigParser()
        config.read(CONFIGFILE)
        openstack.user = config.get(OPENSTACK_SECTION, USER, None)
        openstack.password = config.get(OPENSTACK_SECTION, PASSWORD, None)
        openstack.host = config.get(OPENSTACK_SECTION, HOST, None)
        openstack.tenant = config.get(OPENSTACK_SECTION, TENANT, None)
        openstack.region = config.get(OPENSTACK_SECTION, REGION, None)
        openstack.walle_host = config.get(OPENSTACK_SECTION, WALLE_HOST, None)
        openstack.verify = config.get(OPENSTACK_SECTION, WALLE_VERIFY, True)
        openstack.headers = json.loads(config.get(OPENSTACK_SECTION, HEADERS, {}))
        return openstack
    except ConfigParser.NoSectionError:
        pass
    try:
        walleconfig = Configuration
        config = ConfigParser.ConfigParser()
        config.read(CONFIGFILE)
        walleconfig.user = config.get(WALLE_SECTION, USER, None)
        walleconfig.password = config.get(WALLE_SECTION, PASSWORD, None)
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
