import boto
import re
regexp = re.compile(r'(?<=.)[0-9a-zA-Z]{12}(?=.)')

conn = boto.connect_s3()
bucket = conn.get_bucket('datadrivendota')
contents = bucket.list('css/')

for x in contents:
    word = x.name
    if regexp.search(word) is None:
        x.delete()
