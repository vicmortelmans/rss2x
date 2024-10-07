#!/usr/bin/env python
from dotenv import load_dotenv
import requests
import argparse
import os

# Hardcoded app ID and app secret
load_dotenv(os.getenv('HOME') + "/.rss2fb_env")  # contains app id and app secret
APP_ID = os.environ["FB_APP_ID"]
APP_SECRET = os.environ["FB_APP_SECRET"]

def get_long_lived_access_token(short_lived_token):
    url = "https://graph.facebook.com/v16.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'fb_exchange_token': short_lived_token
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exchange a short-lived Facebook access token for a long-lived one.")
    
    # Only the short-lived token will be provided as an argument
    parser.add_argument("short_lived_token", help="Your short-lived Facebook access token")
    
    args = parser.parse_args()

    # Get the long-lived access token
    long_lived_token = get_long_lived_access_token(args.short_lived_token)
    
    # Print the result (which includes the long-lived token)
    print(long_lived_token)

