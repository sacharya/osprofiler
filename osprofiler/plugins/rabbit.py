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
        qsize = self.queue.queue_declare().message_count
        msgs = []
        batch = 10 if qsize < 1000 else 100
        for i in xrange(batch):
            msg = self.queue.get()
            if msg is None:
                #logger.debug("Empty queue")
                break;
            else:
                msgs.append(msg.payload)
                msg.ack()
        return msgs
    
    def get_sample(self):
        self.connect("monitor.info")
        data = self.get_messages()
        #if d1 is None:
        #    d1 = {}
        #self.connect("notifications.info")
        #d2 = self.get_messages()
        #if d2 is None:
        #    d2 = {}
        #d4 = dict(d1.items() + d2.items())
        logger.debug("%s " % data)
        return data
