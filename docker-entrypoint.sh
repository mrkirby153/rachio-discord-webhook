#!/bin/sh

set -e

. /venv/bin/activate

exec gunicorn -w 4 --bind 0.0.0.0:8080 --forwarded-allow-ips='*' wsgi:app