#!/bin/bash
exec 1> >(logger -s -t $(basename $0)) 2>&1
cd /home/vic/rss2x
source env/bin/activate
python rss2x.py
