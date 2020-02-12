#!/bin/bash -ex

# Correct virtualenv for execution
#source .virtualenv/bin/activate

#python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py compilemessages

# Execute uwsgi for hosting/running the server
uwsgi --module spbm.wsgi:application \
    --master --pidfile=/tmp/spf-uwsgi.pid \
    --socket=:8435 \
	--uid uwsgi \
	--thunder-lock \
	--enable-threads \
    --processes=1 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    #--home=$SRC/.virtualenv/ \
    --daemonize=logs/website.log \
    --touch-reload=spbm/wsgi.py

