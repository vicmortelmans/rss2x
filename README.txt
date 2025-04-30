Create message on twitter (x.org) and facebook, based on first element in an RSS feed.

Requires two files in home directory (/home/vic is hardcoded) containing keys:

~/.rss2x_env

```
X_API_KEY=
X_API_KEY_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=
```

~/.rss2fb_env

```
FB_PAGE_ID=
FB_APP_ID=
FB_APP_SECRET=
```

To refresh the facebook token (expires after 60 days):
1. In Graph API Explorer, create new user access token (permissions: pages_show_list, pages_read_engagement, pages_manage_posts) and copy to =short_lived_user_token.txt=
2. Delete =tokens.json= if it exists
3. Run =rss2fb.py=
