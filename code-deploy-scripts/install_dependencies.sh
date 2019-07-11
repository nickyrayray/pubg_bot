#!/usr/bin/env bash

cd /app/pubg_bot

pip install virtualenv
virtualenv venv
. venv/bin/activate

pip install -r requirements.txt