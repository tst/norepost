import praw
import urlparse
import time
import datetime
import pytz
import ago
import sqlite3
import os
import sys

# CHANGE THESE
USERNAME = ""
PASSWORD = ""
USER_AGENT = "no repost pls bot by /u/tst__"
SUBREDDIT = "montageparodies"

# STOP CHANGING 

# if USERNAME and PASSWORD isn't set the bot will use the environment variables
# NOREPOST_USER for USERNAME
# NOREPOST_PASSWORD for PASSWORD
if USERNAME == "":
    try:
        USERNAME = os.environ['NOREPOST_USER']
    except KeyError:
        sys.exit("Please add the username or set the environment variable NOREPOST_USER")

if PASSWORD == "":
    try:
        PASSWORD = os.environ['NOREPOST_PASSWORD']
    except KeyError:
        sys.exit("Please add the password or set the environment variable NOREPOST_PASSWORD")


# login to Reddit
r = praw.Reddit(user_agent=USER_AGENT)
r.login(USERNAME, PASSWORD)


# get the newest submissions
new_sub = r.get_subreddit(SUBREDDIT).get_new()

conn = sqlite3.connect('/home/tim/norepost/db.db')
c = conn.cursor()

# create the table if it doesn't exist
c.execute("CREATE TABLE IF NOT EXISTS kush (id TEXT);");

# check every new submission
for x in new_sub:
    
    c.execute("SELECT id FROM kush WHERE id = ?", (x.id,))
    if c.fetchone() is not None:
        continue # skip

    
    # special case for youtube URLs
    results = None
    if x.domain == "youtube.com" or x.domain == "m.youtube.com":
        up = urlparse.urlparse(x.url)
        try:
            yid = urlparse.parse_qs(up.query)['v'][0]

        except KeyError: # attribution URL from youtube
            qurl = urlparse.parse_qs(up.query)['u'][0]
            yid = urlparse.parse_qs(qurl)['/watch?v'][0]

        #print ">", x.url, x.title, yid
        results = r.search('url:"' + yid + '"', subreddit=SUBREDDIT)

    elif x.domain == "youtu.be":
        up = urlparse.urlparse(x.url)
        yid = up.path[1:]
        results = r.search('url:"' + yid + '"', subreddit=SUBREDDIT)
    else:
        results = r.search('url:"' + x.url + '"', subreddit=SUBREDDIT)
        
    found = []
    for y in results:
        if y.id == x.id:
            continue
        else:
            # calculate time diff
            created = datetime.datetime.fromtimestamp(y.created_utc, pytz.UTC).replace(tzinfo=None)
            now = datetime.datetime.utcnow()
            diff = ago.human(now - created, precision = 1)
            found.append((diff, " ".join(y.title.splitlines()), y.ups, y.downs, y.permalink))

    if found:
        m = """Yo dank bro. It seems that some scrubs uploaded this MLG footage b4 u:"""
        for f in found:
            m += "\n\n * [%s] [%s (+%i|%i)](%s)" % f
        m += "\n\ni cry evertim :((((" 
        m += "\n\n****"
        m += "\n\n^(I'm currently testing this bot. Q&A @ /u/tst__)."

        #print m
        x.add_comment(m)

    
    # create entry in db
    c.execute("INSERT INTO kush VALUES (?)", (x.id, ))
    conn.commit()

    time.sleep(8)
    #print "*" * 20

conn.close()
