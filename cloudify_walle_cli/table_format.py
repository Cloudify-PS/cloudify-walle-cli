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


def _short_line(name, size):
    if not name:
        return ""
    if len(name) < size:
        return name
    else:
        return name[:size-3] + "..."


def print_header(colums):
    line = ""
    for (name, size) in colums:
        line += (
            "%" + str(size) + "s|"
        ) % (_short_line(name, size))
    print line
    line = ""
    for (_, size) in colums:
        line += "-" * size + "+"
    print line


def print_row(data, colums):
    line = ""
    for (name, size) in colums:
        value = data.get(name)
        line += (
            "%" + str(size) + "s|"
        ) % (_short_line(value, size))
    print line
