#!/bin/bash

set -e

PIDFILE='/apps/vreports/web/vreports.pid'

if [ ! -s "$PIDFILE" ]; then
    echo 'Error: vReports Gunicorn is not running'
    exit 1
fi

pid=$(<"$PIDFILE")
if ! kill -0 "$pid" 2>/dev/null; then
    echo "Error: stale vReports PID file ($pid)"
    exit 1
fi

kill -TERM "$pid"
echo 'vReports Gunicorn stop requested'
