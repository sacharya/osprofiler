import ConfigParser
import MySQLdb
import os

class Mysql:

    def __init__(self, config):
        self.config = config

    def connect(self):
        host = "127.0.0.1"
        user = self.config['auth']['username']
        password = self.config['auth']['password']
        return MySQLdb.connect(host=host, user=user, passwd=password)

    def processlist(self, conn):
        conn.query("show full processlist")
        for row in conn.store_result().fetch_row(maxrows=200, how=1):
            print row

    def status(self, conn):
        conn.query("show global status")
        for row in conn.store_result().fetch_row(maxrows=0):
            print row

    def cluster_status(self, conn):
        #conn.query("show status like 'wsrep%'")
        conn.query("show status like 'wsrep_cluster%'")
        for row in conn.store_result().fetch_row(maxrows=0):
            print row

    def get_sample(self):
        print self.__class__.__name__ + ".get_sample"
        conn = self.connect()
        #self.status(conn)
        #self.cluster_status(conn)
        #self.processlist(conn)

