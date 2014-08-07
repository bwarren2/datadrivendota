web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
worker: celery worker --app=datadrivendota -E -Q default,api_call,management,rpr,db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota
db_worker: celery worker --app=datadrivendota -E -Q db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota

