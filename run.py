#!/usr/bin/env python
import tweepy, feedparser, sqlite3, json, traceback, sys, json, textwrap

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

def post(entry, config):

    message = config["prefix"]
    message += entry.title
    
    linklen = min(len(entry.link),len(entry.id))
     
    if len(message) + linklen > 139:
        # message is too long
        message = textwrap.wrap(message,136)[0] + "..."
        
    message += " "
    
    if len(message) + len(entry.link) > 140:
        message += entry.id
    else:
        message += entry.link    
        
    auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['oauth_token'], config['oauth_token_secret'])
    api = tweepy.API(auth)
    print "posting [%s]" % message.encode("ascii","replace")
    api.update_status(message)

conffile = 'config.json'
if len(sys.argv) == 2:
	conffile=sys.argv[1]

config = json.load(file(conffile))
seen = sqlitedict(config["db"], config["table"])
feed = feedparser.parse(config["feed"])
for e in reversed(feed.entries):
    if not e.id in seen:
        try:
            post(e, config)
        except Exception as ex:
            print "post %s failed" % e.id
            try:
                twittererror = json.loads(ex.read())
                if twittererror["error"] == "Status is a duplicate.":
                    print "duplicate! marking as seen anyway"
                    seen[e.id]=1
                    continue
            except:
                print ex
                continue
        seen[e.id]=1

