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
import utils
import pluginbase

logger = logging.getLogger('osprofiler.%s' % __name__)


class Mysql(pluginbase.PluginBase):

    def __init__(self, *args, **kwargs):
        super(Mysql, self).__init__(*args, **kwargs)

    def galera_status_check(self, arg):
        proc = subprocess.Popen(shlex.split(arg),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=False)

        out, err = proc.communicate()
        ret = proc.returncode
        return ret, out, err

    def generate_query(self, host, port):
        if host:
            host = ' -h %s' % host
        else:
            host = ''

        if port:
            port = ' -P %s' % port
        else:
            port = ''

        return ('/usr/bin/mysql --defaults-file=/home/stack/.my.cnf'
                '%s%s -e "SHOW STATUS WHERE Variable_name REGEXP '
                "'^(wsrep.*|Threads|queries)'\"") % (host, port)

    def get_sample(self):
        sample = {
            "hostname": self.host_id,
            "agent_name": self.config['name'],
            "metrics": list()
        }

        host = "127.0.0.1"
        port = "3306"
        retcode, output, err = self.galera_status_check(
            self.generate_query(host, port)
        )

        if retcode > 0:
            logger.exception(str(err))

        if not output:
            raise Exception(
                'No output received from mysql. Cannot gather metrics.')

        show_status_list = output.split('\n')[1:-1]
        for i in show_status_list:
            val = i.split('\t')[1]
            val = utils.number_or_string(val)
            entry = {i.split('\t')[0]: val}
            sample['metrics'].append(entry)
        logger.debug(sample)
        return sample
