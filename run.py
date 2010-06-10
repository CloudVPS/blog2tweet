#!/usr/bin/env python
import twitter, feedparser, sqlite3, json, traceback, sys

class sqlitedict(object):
    """sqlite table-backed dict emulation"""
    def __init__(self, db, table):
        super(sqlitedict, self).__init__()
        self.db = db
        self.table = table
        self.conn = sqlite3.connect(db)
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS %s (k,v)" % self.table)
    
    def __getitem__(self, k):
        c = self.conn.cursor()
        c.execute("SELECT v FROM %s WHERE k=?" % self.table, (k,))
        for row in c:
            print row
        pass

    def __setitem__(self, k, v):
        c = self.conn.cursor()
        c.execute("INSERT INTO %s (k,v) VALUES(?,?) " % self.table, (k,v))
        self.conn.commit()

    def __contains__(self, k):
        c = self.conn.cursor()
        c.execute("SELECT v FROM %s WHERE k=?" % self.table, (k,))
        for row in c:
            return True
        return False

def post(entry, user, password):
    t = 140
    t = t - len(entry.id) - 1
    title = 'Nieuwe XLS blogpost: '
    title = title + entry.title[0:t-len(title)] + " "
    title = title + entry.id
    api = twitter.Api(username=user, password=password)
    print "posting [%s]" % title
    api.PostUpdate(title)

config = json.load(file('config.json'))
seen = sqlitedict(config["db"], config["table"])
feed = feedparser.parse(config["feed"])
for e in reversed(feed.entries):
    if not e.id in seen:
        try:
            post(e, config["twitteruser"], config["twitterpassword"])
        except:
            print "post %s failed" % e.id
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exc(1)
            continue
        seen[e.id]=1

