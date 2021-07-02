#!/bin/bash

# look for
PROG="/home/dlink/vreports/.venv/bin/gunicorn"

# cmd to find process
cmd="ps -ef | grep $PROG | grep -v -e grep -e tail"

# cmd to get their pids
cmd2="$cmd | awk '{print \$2}'"

# show processes
eval $cmd

# get pids
pids=`eval $cmd2`

# check if we have pids
if [ -z "$pids" ] ; then
    echo Error: $PROG not running
    exit 1
fi

# kill them
kill -9 $pids

# report success or fail
if [ $? -ne 0 ]; then
    echo 'Fail'
else
    echo 'Success'
fi
