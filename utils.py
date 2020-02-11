import re

RE_TWITTER_TWEET_ID = re.compile('^https\:\/\/twitter.com\/.*\/status\/(\d+).*')


def parse_id(tweet_url):
    match = RE_TWITTER_TWEET_ID.match(tweet_url)
    return match.group(1) if match is not None else None
