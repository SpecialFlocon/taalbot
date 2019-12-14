#!/bin/bash

mkdir /home/taalbot/src
ln -s /srv/taalbot/taalbot /home/taalbot/src/taalbot
cd /home/taalbot
exec python3 -m pytest tests
