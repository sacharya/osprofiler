# Copyright 2015, Rackspace US, Inc.
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
import pluginbase

import requests

OVERVIEW_URL = "http://%s:%s/api/overview"
NODES_URL = "http://%s:%s/api/nodes"
CONNECTIONS_URL = "http://%s:%s/api/connections"

OVERVIEW_METRICS = {"object_totals": ["channels",
                                      "connections",
                                      "consumers",
                                      "exchanges",
                                      "queues"],
                    "queue_totals": ["messages",
                                     "messages_ready",
                                     "messages_unacknowledged"],
                    "message_stats": ["get",
                                      "ack",
                                      "confirm",
                                      "deliver_get",
                                      "deliver",
                                      "publish"]}
NODES_METRICS = ["proc_used",
                 "proc_total",
                 "fd_used",
                 "fd_total",
                 "sockets_used",
                 "sockets_total",
                 "mem_used",
                 "mem_limit",
                 "mem_alarm",
                 "disk_free",
                 "disk_free_alarm",
                 "disk_free_limit",
                 "uptime",
                 "run_queue"]

UNIT_MAPPING = {"uptime": 'ms',
                "mem_used": 'bytes',
                "mem_limit": 'bytes',
                "disk_free_limit": "bytes",
                "disk_free": "bytes"}

logger = logging.getLogger('osprofiler.%s' % __name__)


class Rabbit(pluginbase.PluginBase):

    def __init__(self, **kwargs):
        super(Rabbit, self).__init__(**kwargs)

    def get_response(self):
        data = []
        s = requests.Session()
        s.auth = (self.config['auth']['username'],
                  self.config['auth']['password'])
        r = None
        try:
            conn_url = CONNECTIONS_URL % (self.config['auth']['host'],
                                          self.config['auth']['port'])
            r = s.get(conn_url)
        except requests.exceptions.ConnectionError as e:
            logger.exception(str(e))

        if r.ok:
            resp_json = r.json()

        try:
            r = s.get(OVERVIEW_URL % (self.config['auth']['host'],
                                      self.config['auth']['port']))
        except requests.exceptions.ConnectionError as e:
            logger.exception(str(e))

        if r.ok:
            resp_json = r.json()
            for k in OVERVIEW_METRICS:
                if k in resp_json:
                    for a in OVERVIEW_METRICS[k]:
                        if a in resp_json[k]:
                            data.append(self.metric_dict(
                                self.metric_name(a),
                                resp_json[k][a],
                                UNIT_MAPPING.get('%s' % a))
                            )

        try:
            r = s.get(NODES_URL % (self.config['auth']['host'],
                                   self.config['auth']['port']))
        except requests.exceptions.ConnectionError as e:
            logger.exception(str(e))

        if r.ok:
            resp_json = r.json()
            for k in NODES_METRICS:
                data.append(self.metric_dict(
                    self.metric_name(k),
                    resp_json[0][k],
                    UNIT_MAPPING.get('%s' % k))
                )
        return data

    def get_sample(self):
        logger.info("RabbitMQ Sampling")
        sample = {
            "hostname": self.host_id,
            "agent_name": self.config.get('name', 'rabbit'),
            "metrics": list()
        }
        sample['metrics'].extend(self.get_response())
        return sample
