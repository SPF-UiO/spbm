#!/bin/sh

exec gunicorn \
  --config=/gunicorn.conf \
  cyb_oko.wsgi:application
