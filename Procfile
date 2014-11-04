web: newrelic-admin run-program waitress-serve --port $PORT datadrivendota.wsgi:application
worker: celery worker --app=datadrivendota -E -Q default,api_call,management,rpr,db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota
db_worker: celery worker --app=datadrivendota -E -Q db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota
