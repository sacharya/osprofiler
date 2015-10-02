import kombu
import logging
import pluginbase

logger = logging.getLogger('osprofiler.%s' % __name__)


class Events(pluginbase.PluginBase):

    def __init__(self, **kwargs):
        super(Events, self).__init__(**kwargs)

    def connect(self, name):
        if 'host' in self.config['auth']:
            hostname = self.config['auth']['host']
        else:
            hostname = "localhost"
        if 'port' in self.config['auth']:
            port = self.config['auth']['port']
        else:
            port = 5672
        userid = self.config['auth']['username']
        password = self.config['auth']['password']
        self.conn = kombu.BrokerConnection(hostname=hostname, port=port,
                                           userid=userid, password=password,
                                           virtual_host="/")
        self.exchange = kombu.Exchange(name, type='topic',
                                       durable=False,
                                       channel=self.conn.channel())
        routing_key = name
        self.queue = kombu.Queue(name=routing_key, routing_key=routing_key,
                                 exchange=self.exchange,
                                 channel=self.conn.channel(),
                                 durable=False)
        self.queue.declare()

    def get_messages(self):
        qsize = self.queue.queue_declare().message_count
        msgs = []
        batch = 10 if qsize < 1000 else 100
        for i in xrange(batch):
            msg = self.queue.get()
            if msg is None:
                # logger.debug("Empty queue")
                break
            else:
                msgs.append(msg.payload)
                msg.ack()
        return msgs

    def get_sample(self):
        logger.info("Events sampling")
        self.connect("monitor.info")
        data = self.get_messages()
        logger.debug("%s " % data)
        return data
