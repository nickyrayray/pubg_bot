#!/usr/bin/env bash

cd /app/pubg_bot

. venv/bin/activate

gunicorn server.pubg_server:app