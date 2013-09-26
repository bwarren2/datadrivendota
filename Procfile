web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
api_worker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO -Q api_call
non_api_worker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO -Q db_upload,default

