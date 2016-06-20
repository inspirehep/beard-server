web: gunicorn beard_server.app -c gunicorn.cfg
worker: celery worker -A beard_server -l INFO -P solo -Q beard
