web: cd datadrivendota && newrelic-admin run-program waitress-serve --port $PORT datadrivendota.wsgi:application
worker: celery worker --app=datadrivendota -E -Q integrity,default,api_call,rpr,db_upload --loglevel=INFO  -c 3  --workdir=datadrivendota
db_worker: celery worker --app=datadrivendota -E -Q db_upload --loglevel=WARNING  -c 3  --workdir=datadrivendota
beatnik_worker: celery worker --app=datadrivendota -E -Q default,api_call,integrity,rpr,db_upload --loglevel=INFO  -c 3  -B --workdir=datadrivendota
parsing_worker: celery worker --app=datadrivendota -E -Q parsing --loglevel=INFO  -c 3  -B --workdir=datadrivendota
