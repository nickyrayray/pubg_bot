#!/usr/bin/env bash

cd /home/ec2-user/apps/pubg_bot

pip install virtualenv
virtualenv venv
. venv/bin/activate

pip install -r requirements.txt