web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
worker: newrelic-admin run-program python project/manage.py celeryd -E -B --loglevel=INFO
