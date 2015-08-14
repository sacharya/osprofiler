import ConfigParser
import MySQLdb
import os

##TODO: Put this into a class.

def connect(conf="~/.my.cnf", section="mysql"):
    parser = ConfigParser.SafeConfigParser(allow_no_value=True)
    parser.read([os.path.expanduser("~/.my.cnf")])
    host = parser.get(section, 'host')
    user = parser.get(section, 'user')
    password = parser.get(section, 'password')
    return MySQLdb.connect(host=host, user=user, passwd=password)

def processlist(conn):
    conn.query("show full processlist")
    for row in conn.store_result().fetch_row(maxrows=200, how=1):
        print row

def status(conn):
    conn.query("show global status")
    for row in conn.store_result().fetch_row(maxrows=0):
        print row

def cluster_status(conn):
    #conn.query("show status like 'wsrep%'")
    conn.query("show status like 'wsrep_cluster%'")
    for row in conn.store_result().fetch_row(maxrows=0):
        print row

def main():
    conn = connect()
    status(conn)
    cluster_status(conn)
    processlist(conn)

if __name__ == '__main__':
    main()