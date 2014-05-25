import praw
import urlparse
import time
import datetime
import pytz
import ago
import sqlite3
import os
import sys
from handle_config import *

class Bot:
    def __init__(self):
        """logins into reddit, established a database (connect) and creates
           the table if necessary"""

        # login to Reddit
        self.r = praw.Reddit(user_agent=USER_AGENT)
        self.r.login(USERNAME, PASSWORD)

        # establish database 
        self.conn = sqlite3.connect(os.path.join(PATHTO,"db.db"))
        self.c = self.conn.cursor()

        # create the table if it doesn't exist
        self.c.execute("CREATE TABLE IF NOT EXISTS kush (id TEXT);");
    
    def is_checked(self, x):
        """Checks if a submission was already checked"""
        self.c.execute("SELECT id FROM kush WHERE id = ?", (x.id,))
        if self.c.fetchone() is not None:
            return True
        else:
            return False

    def news_loop(self):
        """Gets the newest submissions, checks if they were handled in the past
           and apply our functions"""

        # get the newest submissions
        new_sub = self.r.get_subreddit(SUBREDDIT).get_new()
        
        # check every new submission
        for x in new_sub:
            # Skip the submission if it's already checked
            if self.is_checked(x):
                continue
            
            token = self.parse_url(x)
            found = self.find_results(x, token)
            self.post_comment(x, found)
            self.add_checked(x)


    def parse_url(self, x):
        """Takes a comment object and tries to extract the youtube video ID
           if that is not possible it will just return the URL instead of
           the ID"""

        # special case for youtube URLs
        # it will extract the youtube ID and return it
        if x.domain in ["youtube.com", "m.youtube.com"]:
            up = urlparse.urlparse(x.url)
            try:
                yid = urlparse.parse_qs(up.query)['v'][0]
            except KeyError: # attribution URL from youtube
                qurl = urlparse.parse_qs(up.query)['u'][0]
                yid = urlparse.parse_qs(qurl)['/watch?v'][0]
            finally:
                return yid
        
        elif x.domain == "youtu.be":
            up = urlparse.urlparse(x.url)
            yid = up.path[1:]
            return yid
        
        else:
            # just return the submitted url
            return x.url
            
    
    def get_human_time_diff(self, y):
        """Returns a time diff in human readable form, e.g.
           42 minutes ago
           3 hours ago
           24 days ago"""
        # translates to UTC so that the time isn't location-dependend
        created = datetime.datetime.fromtimestamp(y.created_utc, pytz.UTC).replace(tzinfo=None)
        now = datetime.datetime.utcnow()
        diff = ago.human(now - created, precision = 1)
        return diff


    def find_results(self, x, token):
        """Takes a comment object and a token which is returned by parse_url()
           It uses reddit's search function to find submissions in the same
           subreddit with the same token (either Youtube video ID or URL).
           It returns a list for each result which includes a tuple including:
           
           * time difference
           * title
           * upvotes
           * downvotes
           * permalink"""

        # get results
        results = self.r.search('url:"' + token + '"', subreddit=SUBREDDIT)
        # examine the results found from doing a search
        found = []
        for y in results:
            # reject the result if it's the same id as the examined submission
            # i.e. found the result which we are looking at
            if y.id == x.id:
                continue
            # reject if the examined submission is older than the found one
            elif x.created_utc < y.created_utc:
                continue
            else:
                human_time = self.get_human_time_diff(y)
                title = " ".join(y.title.splitlines())
                found.append((human_time, title, y.ups, y.downs, y.permalink))
        return found
    
    def post_comment(self, x, found):
        """Posts a comment on a comment object (x) using the output from
           find_results"""

        # if we found reposts we're going to add a comment to the submission
        if found:
            m = COMMENT_INTRODUCTION
            for f in found:
                m += "\n\n * [%s] [%s (+%i|%i)](%s)" % f
            m += "\n\n"
            m += COMMENT_ENDING
            
            # if debug=on then don't actually post a comment
            if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                logging.debug(m)
            else:
                x.add_comment(m)

    def add_checked(self, x):
        """Adds comment id to the database so that it won't be checked in
           the future again"""
        # Insert id into the database to that it won't be rechecked
        self.c.execute("INSERT INTO kush VALUES (?)", (x.id, ))
        self.conn.commit()

    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    
bot = Bot()
bot.news_loop()
bot.close()
