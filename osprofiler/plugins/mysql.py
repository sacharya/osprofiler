#!/usr/bin/env python

# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import shlex
import subprocess
import pluginbase

from osprofiler import utils

logger = logging.getLogger('osprofiler.%s' % __name__)


class Mysql(pluginbase.PluginBase):

    def __init__(self, **kwargs):
        super(Mysql, self).__init__(**kwargs)

    def galera_status_check(self, arg):
        proc = subprocess.Popen(shlex.split(arg),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=False)

        out, err = proc.communicate()
        ret = proc.returncode
        return ret, out, err

    def generate_query(self):
        defaults_file = self.config.get('auth').get('defaults-file')
        host = self.config.get('auth').get('host', '127.0.0.1')
        port = self.config.get('auth').get('port', '3306')
        port = ' -P %s' % port if port else ''
        host = ' -h %s' % host if host else ''
        mysql_query = """SHOW STATUS WHERE Variable_name REGEXP
                         '^(wsrep.*|Threads|queries)'"""
        if defaults_file is None:
            username = self.config.get('auth').get('username', 'root')
            password = self.config.get('auth').get('password', 'admin')
            username = '-u%s' % username if username else ''
            password = '-p%s' % password if password else ''
            query = 'mysql %s %s %s %s -e \"%s\"' % (username, password,
                                                     host, port, mysql_query)
        else:
            query = 'mysql --defaults-file=%s %s%s -e \"%s\"' % (defaults_file,
                                                                 host, port,
                                                                 mysql_query)
        print query
        return query

    def get_sample(self):
        sample = {
            "hostname": self.host_id,
            "agent_name": self.config.get('name', 'mysql'),
            "metrics": list()
        }

        retcode, output, err = self.galera_status_check(
            self.generate_query()
        )

        if retcode > 0:
            logger.error(str(err))

        if not output:
            raise Exception(
                'No output received from mysql. Cannot gather metrics.')

        show_status_list = output.split('\n')[1:-1]
        for line in show_status_list:
            key, val = line.rsplit("\t", 1)
            val = utils.number_or_string(val)
            sample['metrics'].append({
                'name': self.metric_name(key),
                'value': val
            })
        return sample
