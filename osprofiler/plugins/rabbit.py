import handlers
import kombu
import pluginbase

class Rabbit(pluginbase.PluginBase):

    def __init__(self, *args, **kwargs):
        super(Rabbit, self).__init__(args, kwargs)

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
        i=0
        while True:
            print type(self.queue)
            msg = self.queue.get()
            if msg is None:
                break;
            i += 1
            log = False
            if log:
                print "="*25
                print i
                import pprint
                pprint.pprint(msg.payload)
                print msg.acknowledged
                print msg.payload['_unique_id']
                print msg.payload['message_id']
                print msg.payload['event_type']
            return msg.payload

    def get_sample(self):
        super(Rabbit, self).get_sample()
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
        print d4
        print "Leaving " + self.__class__.__name__ + ".get_sample"
        return d4
