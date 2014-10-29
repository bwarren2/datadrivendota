web: newrelic-admin run-program gunicorn -b 0.0.0.0:$PORT -w 9 -k gevent --max-requests 250 --pythonpath datadrivendota --preload datadrivendota.wsgi
worker: celery worker --app=datadrivendota -E -Q default,api_call,management,rpr,db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota
db_worker: celery worker --app=datadrivendota -E -Q db_upload --loglevel=WARNING  -c 6  --workdir=datadrivendota
