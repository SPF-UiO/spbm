#!/bin/sh

uwsgi --chdir=/home/spf/spf_web/ \
--module spf_web.wsgi:application \
--master --pidfile=/tmp/spf-uwsgi.pid \
--socket=127.0.0.1:8435 \
--processes=1 \
--harakiri=20 \
--max-requests=5000 \
--vacuum \
--home=/home/spf/spf_web/virtualenv/ \
--daemonize=/home/spf/logs/website.log \
--touch-reload=/home/spf/spf_web/wsgi.py

