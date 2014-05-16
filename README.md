# Norepost bot for reddit

## Installation

The bot runs on Python 2.7 with the following packages:

* [PRAW aka. Python Reddit API Wrapper](https://github.com/praw-dev/praw)
* [pytz](http://pytz.sourceforge.net/)
* [ago](https://pypi.python.org/pypi/ago/0.0.6)

which can be easily installed using pip

    pip install praw pytz ago

## Usage

If you execute the bot.py with

    python bot.py

it will crawl the /new page and check each new post for a repost using the search function. It provides a special function for youtube videos through extracting the video ID.


## Requests / Questions

If you have any requests or actions feel free to open an issue or write me a email.
