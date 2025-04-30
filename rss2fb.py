import os
import feedparser
import json
import logging
import time
import requests
from sys import stdout
from flask import Flask, request, redirect
from datetime import datetime, timedelta
from facebook import GraphAPI
from dotenv import load_dotenv

logger = logging.getLogger("rss2fb_renewing")
handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

load_dotenv(os.getenv('HOME') + "/.rss2fb_env")

APP_ID = os.getenv("FB_APP_ID")
APP_SECRET = os.getenv("FB_APP_SECRET")
PAGE_ID = os.getenv("FB_PAGE_ID")
REDIRECT_URI = os.getenv("FB_REDIRECT_URI")

TOKENS_FILE = "tokens.json"
USER_TOKEN_EXPIRY_DAYS = 60
SCOPES = ["pages_manage_posts", "pages_read_engagement", "pages_show_list", "public_profile"]

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE) as f:
            return json.load(f)
    return {}

def save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_expired(timestamp):
    return time.time() > timestamp - 86400  # renew a day early

def get_long_lived_token(short_token):
    url = "https://graph.facebook.com/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": short_token,
    }
    response = requests.get(url, params=params).json()
    #import pdb; pdb.set_trace()
    logging.info("get_long_lived_token response: " + json.dumps(response)) 
    return response["access_token"]

def get_page_token(user_token):
    url = f"https://graph.facebook.com/v18.0/me/accounts"
    res = requests.get(url, params={"access_token": user_token}).json()
    for page in res.get("data", []):
        if page["id"] == PAGE_ID:
            return page["access_token"]
    raise Exception("Page token not found")

def ensure_valid_tokens():
    tokens = load_tokens()

    if "page_access_token" in tokens and not is_expired(tokens["expires_at"]):
        return tokens["page_access_token"]

    if "user_access_token" not in tokens or is_expired(tokens["user_expires_at"]):
        if not os.path.exists("short_lived_user_token.txt"):
            raise Exception("Please provide a fresh short-lived user token in short_lived_user_token.txt")
        with open("short_lived_user_token.txt") as f:
            short_token = f.read().strip()
        user_token = get_long_lived_token(short_token)
        tokens["user_access_token"] = user_token
        tokens["user_expires_at"] = (datetime.now() + timedelta(days=USER_TOKEN_EXPIRY_DAYS)).timestamp()

    # always refresh page token
    page_token = get_page_token(tokens["user_access_token"])
    tokens["page_access_token"] = page_token
    tokens["expires_at"] = (datetime.now() + timedelta(days=USER_TOKEN_EXPIRY_DAYS)).timestamp()

    save_tokens(tokens)
    return page_token

# ========================
# Example daily post
# ========================
if __name__ == "__main__":

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

    # The message you want to post on the Facebook page
    message = f"{title}\n{link}"

    # The path to the image you want to upload (local file)
    image_path = 'image_name.png'

    # Initialize the connection to the Facebook Graph API
    token = ensure_valid_tokens()
    graph = GraphAPI(access_token=token)
    page_id = os.environ["FB_PAGE_ID"]

    # Post the image with the message directly to the page feed
    try:
        with open(image_path, 'rb') as image_file:
            post = graph.put_photo(
                image=image_file,
                message=message,
                album_path=f'{page_id}/photos'  # Posts image to page feed
            )
        print(f"Successfully posted image with id: {post['post_id']}")
    except GraphAPIError as e:
        print(f"Error: {e}")
