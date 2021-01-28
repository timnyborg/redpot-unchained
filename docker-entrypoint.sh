#!/bin/sh
python manage.py collectstatic --no-input --clear

# Runs the CMD in the dockerfile, e.g. uwsgi
exec "$@"