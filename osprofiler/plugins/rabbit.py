import kombu

class Rabbit:

    def __init__(self, config):
        self.config = config
        
    def connect(self, name):
        self.conn = kombu.BrokerConnection(hostname="localhost", port=5672, userid='guest', password='guest', virtual_host="/")
        self.exchange = kombu.Exchange(name, type='topic', durable=False, channel=self.conn.channel())
        #print self.exchange
        routing_key = name
        self.queue = kombu.Queue(name=routing_key, routing_key=routing_key, exchange=self.exchange, channel=self.conn.channel(), durable=False)
        self.queue.declare()
    
    def get_messages(self):
        i=0
        while True:
            msg = self.queue.get()
            if msg is None:
                break;
            print "="*25
            print i
            i += 1
            import pprint
            pprint.pprint(msg.payload)
            print msg.acknowledged
            print msg.payload['_unique_id']
            print msg.payload['message_id']
            print msg.payload['event_type']
    
    def get_sample(self):
        print self.__class__.__name__ + ".get_sample"
        rabbit = Rabbit("monitor.info")
        #rabbit.get_messages()

        rabbit = Rabbit("notifications.info")
        #rabbit.get_messages()
