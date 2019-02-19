#!/bin/bash -ex

# Correct virtualenv for execution
#source .virtualenv/bin/activate

# Source path -- simple and to the point
SRC=.

# Execute uwsgi for hosting/running the server
uwsgi --module spbm.wsgi:application \
    --master --pidfile=/tmp/spf-uwsgi.pid \
    --socket=127.0.0.1:8435 \
    --processes=1 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    #--home=$SRC/.virtualenv/ \
    --daemonize=$SRC/logs/website.log \
    --touch-reload=$SRC/spbm/wsgi.py

