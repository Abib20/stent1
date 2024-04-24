web: gunicorn cov.wsgi --log-file -
main_worker:  celery -A cov worker --loglevel=info -E -B