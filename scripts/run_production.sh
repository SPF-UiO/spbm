#!/bin/bash -ex

# Correct virtualenv for execution
source .virtualenv/bin/activate

# Execute uwsgi for hosting/running the server
uwsgi --chdir=/home/spf/src/spbm/ \
--module spbm.wsgi:application \
--master --pidfile=/tmp/spf-uwsgi.pid \
--socket=127.0.0.1:8435 \
--processes=1 \
--harakiri=20 \
--max-requests=5000 \
--vacuum \
--module spbm.wsgi:application \
--master --pidfile=/tmp/spf-uwsgi.pid \
--socket=127.0.0.1:8435 \
--processes=1 \
--harakiri=20 \
--max-requests=5000 \
--vacuum \
--home=/home/spf/src/.virtualenv/ \
--daemonize=/home/spf/logs/website.log \
--touch-reload=wsgi.py

