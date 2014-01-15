web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
worker: celery worker --app=datadrivendota.celery -E -Q db_upload,default,api_call,management,rpr --loglevel=INFO  -c 1
