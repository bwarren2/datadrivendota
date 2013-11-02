web: newrelic-admin run-program python datadrivendota/manage.py run_gunicorn -b 0.0.0.0:$PORT
apiWorker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO -Q api_call -c 2
nonApiWorker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO -Q db_upload,default  -c 2
worker: python datadrivendota/manage.py celeryd -E  --loglevel=INFO -Q db_upload,default,api_call -c 2
