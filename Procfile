web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
worker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO
