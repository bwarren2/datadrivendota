web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
worker: newrelic-admin run-program python datadrivendota/manage.py celery worker -E
