#!/bin/bash

PIDFILE='/apps/vreports/web/vreports.pid'

if [ ! -s "$PIDFILE" ]; then
    echo 'vReports Gunicorn is not running'
    exit 1
fi

pid=$(<"$PIDFILE")
if ! kill -0 "$pid" 2>/dev/null; then
    echo "vReports Gunicorn has a stale PID file ($pid)"
    exit 1
fi

echo "vReports Gunicorn is running (PID $pid)"
