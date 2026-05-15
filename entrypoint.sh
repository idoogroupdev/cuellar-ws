#!/bin/sh
set -e

python manage.py migrate
python manage.py setup_roles
python manage.py setup_superuser
python manage.py createcachetable

# Run collectstatic if needed
if [ "$RUN_COLLECTSTATIC" = "True" ]; then
    python manage.py collectstatic --noinput
fi


exec "$@"
