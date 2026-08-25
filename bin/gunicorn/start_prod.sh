#!/bin/bash

set -e

cd /apps/vreports
source /home/dlink/.vreports
source .venv/bin/activate
export PYTHONPATH='/apps/vreports/lib:/apps/vreports/web:/apps/vweb/src:/apps/vlib/src'

cd web
gunicorn --daemon -c gunicorn.conf.py wsgi:app

for attempt in {1..50}; do
    if curl --silent --fail --unix-socket vreports.sock \
            http://localhost/ >/dev/null; then
        echo 'vReports Gunicorn successfully started'
        exit 0
    fi
    sleep 0.1
done

echo 'Error: vReports Gunicorn did not become ready' >&2
exit 1
