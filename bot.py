import praw
import urlparse
import time
import datetime
import pytz
import ago
import sqlite3
import os
import sys

### CHANGE THESE
USERNAME = ""
PASSWORD = ""
USER_AGENT = "no repost pls bot by /u/tst__"
SUBREDDIT = "montageparodies"
# Introduction appears before posting the matching URLs
INTRODUCTION = "Yo dank bro. It seems that some scrubs uploaded this MLG footage b4 u:"
# Ending appears after posting the matching URLS; \n\n for newline
ENDING = """i cry evertim :(((( \n\n**** \n\n^(I'm currently testing this bot. Q&A @ /u/tst__)."""

print INTRODUCTION
print ENDING
### STOP CHANGING 

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
    
    # Skip the submission if it's already checked
    c.execute("SELECT id FROM kush WHERE id = ?", (x.id,))
    if c.fetchone() is not None:
        continue

    
    # special case for youtube URLs
    # it will extract the youtube ID and search for its occurences
    results = None
    if x.domain in ["youtube.com", "m.youtube.com"]:
        up = urlparse.urlparse(x.url)

        try:
            yid = urlparse.parse_qs(up.query)['v'][0]

        except KeyError: # attribution URL from youtube
            qurl = urlparse.parse_qs(up.query)['u'][0]
            yid = urlparse.parse_qs(qurl)['/watch?v'][0]

        results = r.search('url:"' + yid + '"', subreddit=SUBREDDIT)

    elif x.domain == "youtu.be":
        up = urlparse.urlparse(x.url)
        yid = up.path[1:]
        results = r.search('url:"' + yid + '"', subreddit=SUBREDDIT)
    else:
        # just search for the submitted url
        results = r.search('url:"' + x.url + '"', subreddit=SUBREDDIT)
        
    
    # examine the results found from doing a search
    found = []
    for y in results:
        # reject the result if it's the same id as the examined submission
        # i.e. found the result which we are looking at
        if y.id == x.id:
            continue
        else:
            # calculate time diff
            # translates to UTC so that the time isn't location-dependend
            created = datetime.datetime.fromtimestamp(y.created_utc, pytz.UTC).replace(tzinfo=None)
            now = datetime.datetime.utcnow()
            diff = ago.human(now - created, precision = 1)
            found.append((diff, " ".join(y.title.splitlines()), y.ups, y.downs, y.permalink))
    
    # if we found reposts we're going to add a comment to the submission
    if found:
        m = INTRODUCTION
        for f in found:
            m += "\n\n * [%s] [%s (+%i|%i)](%s)" % f
        m += "\n\n"
        m += ENDING

        x.add_comment(m)

    
    # Insert id into the database to that it won't be rechecked
    c.execute("INSERT INTO kush VALUES (?)", (x.id, ))
    conn.commit()

    time.sleep(8)

conn.close()
