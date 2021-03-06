#!/bin/bash -ex

# Correct virtualenv for execution
source .virtualenv/bin/activate

# Ensure requirements are up to date
pip install -Ur requirements.txt

# Execute database migrations
./manage.py migrate

# Collect static files for serving
./manage.py collectstatic --noinput

# Compile translation messages
./manage.py compilemessages -l nb_NO -l en_UK

# Reload uWSGI
if pgrep -U spf uwsgi; then
    touch spbm/wsgi.py
else
    ./scripts/run_production.sh
fi
