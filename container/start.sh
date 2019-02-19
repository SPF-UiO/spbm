#!/bin/sh
exec uwsgi --chdir=/app \
    --module spbm.wsgi:application \
    --master --pidfile=/tmp/spf-uwsgi.pid \
    --socket=0.0.0.0:8435 \
    --processes=1 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    --daemonize=/app/logs/website.log \
    --touch-reload=/app/spbm/wsgi.py
    #--home=$SRC/.virtualenv/ \


#exec uwsgi --ini uwsgi.ini

