#!/usr/bin/env python
from dotenv import load_dotenv
import facebook
import feedparser
import logging
import os
import requests
from sys import stdout

logger = logging.getLogger("rss2fb")
handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

load_dotenv(os.getenv('HOME') + "/.rss2fb_env")  # contains access token

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
# Replace this with your Facebook Page Access Token
page_access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]
page_id = os.environ["FB_PAGE_ID"]

# The message you want to post on the Facebook page
message = f"{title}\n{link}"

# The path to the image you want to upload (local file)
image_path = 'image_name.png'

# Initialize the connection to the Facebook Graph API
graph = facebook.GraphAPI(access_token=page_access_token)

# Post the image with the message directly to the page feed
try:
    with open(image_path, 'rb') as image_file:
        post = graph.put_photo(
            image=image_file,
            message=message,
            album_path=f'{page_id}/photos'  # Posts image to page feed
        )
    print(f"Successfully posted image with id: {post['post_id']}")
except facebook.GraphAPIError as e:
    print(f"Error: {e}")

