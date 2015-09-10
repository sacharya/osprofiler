import handlers
import kombu
import log
import pluginbase

logger = log.get_logger()


class Rabbit(pluginbase.PluginBase):

    def __init__(self, *args, **kwargs):
        super(Rabbit, self).__init__(*args, **kwargs)

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
                durable=False, channel=self.conn.channel())
        routing_key = name
        self.queue = kombu.Queue(name=routing_key, routing_key=routing_key, 
                exchange=self.exchange, channel=self.conn.channel(), 
                durable=False)
        self.queue.declare()

    def get_messages(self):
        msg = self.queue.get()
        if msg is None:
            logger.debug("Empty queue")
            return
        return msg.payload

    def get_sample(self):
        self.connect("monitor.info")
        d0 = {"node":"1", "timestamp":"123", "agent": "mysql"}
        d1 = self.get_messages()
        if d1 is None:
            d1 = {}
        self.connect("notifications.info")
        d2 = self.get_messages()
        if d2 is None:
            d2 = {}
        d4 = dict(d0.items() + d1.items() + d2.items())
        logger.debug("%s " % d4)
        logger.debug("Leaving " + self.__class__.__name__ + ".get_sample")
        return d4
