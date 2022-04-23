"""
I want a Raspberry Pi 4 and I dont want to monitor manually. 
This solves that issue for the most part.
Posts to my discord webhook, substitute your own!
Author: https://twitter.com/medarkus_
"""
import feedparser
import os

from time import sleep
from typing import Dict, NamedTuple
from collections import namedtuple
from discord_webhook import DiscordWebhook
from datetime import datetime, timedelta
from time import mktime


# globals
RSS_FEED = 'https://rpilocator.com/feed/'
POLL_INTERVAL = 61  # only poll once per minute
COUNTRIES = [
    'US',  # murica
    'UK',  # brits
    'CA'  # moose
]
CATEGORY = 'PI4'  # I only want a Pi4
PREV_SEEN = {}
WEBHOOK = os.environ.get('WEBHOOK')
if WEBHOOK is None:
    print(f"I need a Discord Webhook url >:(")
    exit(-1)


def is_valid_entry(entry: Dict) -> bool:
    """
    A valid entry meets the following criteria:
    1) timestamp delta within past 12 hrs
    2) US, UK, or Canada listing
    3) Raspberry Pi 4 category
    """

    # get last 12 hrs
    last_twelve_hrs = (datetime.now() - timedelta(hours=12))
    # convert time blob to proper timestamp so we can compare
    ts = datetime.fromtimestamp(mktime(entry.published_parsed))

    if ts >= last_twelve_hrs and ts < datetime.now():
        return (entry.tags[1].term in COUNTRIES and entry.tags[2].term == CATEGORY)

    return False


def parse_entry(entry: Dict) -> NamedTuple:
    """
    Pull out Title and Link
    """
    title = entry.title
    url = entry.link
    PiAlert = namedtuple('PiAlert', 'title url')

    return PiAlert(title, url)


def post_alert(pi_alert: NamedTuple) -> None:
    """
    Post to discord webhook, only alert/tag  my user
    """
    alert = f"{pi_alert.title}\n{pi_alert.url}"
    msg = f'<@260992607612567553>, {alert}'
    allowed_mentions = {
        "users": ["260992607612567553"]
    }

    wh = DiscordWebhook(url=WEBHOOK, content=msg,
                        allowed_mentions=allowed_mentions)
    _ = wh.execute()


def main() -> None:
    while True:
        # pull feed
        news_feed = feedparser.parse(RSS_FEED)
        for entry in news_feed.entries:
            if is_valid_entry(entry):
                # use timestamp as key in hashmap to track dupes
                # key is timestamp, val is entry object
                ts = entry.published
                if ts in PREV_SEEN:
                    pass
                else:
                    PREV_SEEN[ts] = entry
                    alert = parse_entry(entry)
                    # post to discord
                    post_alert(alert)

        # trying to be a good citizen. rpilocator creator has kindly
        # asked folks to not poll more than once per min
        sleep(POLL_INTERVAL)


main()
