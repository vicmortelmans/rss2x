#!/usr/bin/env python
import asyncio
from dotenv import load_dotenv
import feedparser
import logging
import os
import requests
from sys import stdout
import tweepy

logger = logging.getLogger("rss2x")
handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

load_dotenv(os.getenv('HOME') + "/.rss2x_env")  # contains OPENAI_API_KEY

# Two step approach: https://stackoverflow.com/a/76542868/591336

# Authenticate to Twitter API for user 'AlledaagsG'
auth = tweepy.OAuth1UserHandler(os.environ["X_API_KEY"],os.environ["X_API_KEY_SECRET"])
auth.set_access_token(os.environ["X_ACCESS_TOKEN"],os.environ["X_ACCESS_TOKEN_SECRET"])
alledaagsg_tweepy_client_v1 = tweepy.API(auth)
alledaagsg_tweepy_client_v2 = tweepy.Client(None,os.environ["X_API_KEY"],os.environ["X_API_KEY_SECRET"],os.environ["X_ACCESS_TOKEN"],os.environ["X_ACCESS_TOKEN_SECRET"])
alledaagsg_tweepy_client_v2.get_me() 

# Parse feed
feed = feedparser.parse("https://alledaags.gelovenleren.net/dailyfeed.rss")
title = feed.entries[0].title
link = feed.entries[0].link
description = feed.entries[0].description
image_url = feed.entries[0].enclosures[0]['href']

# Download image
img_data = requests.get(image_url).content
with open('image_name.png', 'wb') as handler:
    handler.write(img_data)

# Create media
media = alledaagsg_tweepy_client_v1.media_upload(filename='image_name.png')
media_id = media.media_id
print(title, link, description, image_url, media_id)

#alledaagsg_tweepy_client_v2.create_tweet(text="Tweet text", media_ids=[media_id])
