#!/bin/bash -ex

# Correct virtualenv for execution
source .virtualenv/bin/activate

# Ensure requirements are up to date
pip install -r requirements.txt

# Execute database migrations
./manage.py migrate

# Collect static files for serving
./manage.py collectstatic --noinput

# Compile translation messages
./manage.py compilemessages

# Reload uWSGI
touch spbm/wsgi.py
