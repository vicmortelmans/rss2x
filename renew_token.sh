#!/bin/bash
echo "Paste your short-lived user token:"
read token
echo "$token" > short_lived_user_token.txt
rm -f tokens.json
echo "New token saved. Run your script now to refresh the token."

