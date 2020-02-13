#!/bin/bash -e

if [[ ! "$DEBUG" ]]; then
  echo "Migrating database due to SPBM_DEBUG being false"
  python manage.py showmigrations --plan
  python manage.py migrate
fi

# Normally execute uwsgi for hosting/running the server
exec "$@"
