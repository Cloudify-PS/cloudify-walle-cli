########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from setuptools import setup

setup(
    name='cloudify_wallie',
    version='1.4a2',
    author='Gigaspaces',
    author_email='cosmo-admin@gigaspaces.com',
    packages=['cloudify_wallie_cli'],
    license='LICENSE',
    description='Cloudify CLI for Wallie service',
    entry_points={
        'console_scripts': [
            'walliecfy = cloudify_wallie_cli.cli:main']
    },
    install_requires=[
        'cloudify-rest-client',
        'cloudify-dsl-parser',
        'click'
    ]
)
