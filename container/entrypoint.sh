#!/bin/bash -ex

# Correct virtualenv for execution
#source .virtualenv/bin/activate

#python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py compilemessages

# Execute uwsgi for hosting/running the server
uwsgi --ini container/uwsgi.ini
