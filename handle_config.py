import ConfigParser
import logging
import sys
import os

PATHTO = os.path.dirname(os.path.realpath(__file__))

config = ConfigParser.SafeConfigParser()
config.read(os.path.join(PATHTO, "config.ini"))

## get variables
USERNAME = config.get("reddit", "username")
PASSWORD = config.get("reddit", "password")
USER_AGENT = config.get("technical", "user_agent")
SUBREDDIT = config.get("reddit", "subreddit")
# XXX replace workarounds for reddit => one new line transformed to two
COMMENT_INTRODUCTION = config.get("comment", "introduction", raw = True).replace("\n", "\n\n")
COMMENT_ENDING = config.get("comment", "ending", raw = True).replace("\n", "\n\n")

if config.get("technical", "debug") == "on":
    logging.basicConfig(level=logging.DEBUG) 
else:
    logging.basicConfig(level=logging.ERROR) 

# if USERNAME and PASSWORD isn't set the bot will use the environment variables
if USERNAME in ["username", ""]:
    try:
        USERNAME = os.environ['NOREPOST_USERNAME']
    except KeyError:
        sys.exit("Please add the username or set the environment variable NOREPOST_USERNAME")

if PASSWORD in ["password", ""]:
    try:
        PASSWORD = os.environ['NOREPOST_PASSWORD']
    except KeyError:
        sys.exit("Please add the password or set the environment variable NOREPOST_PASSWORD")

