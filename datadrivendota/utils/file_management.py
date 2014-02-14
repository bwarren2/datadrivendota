import json
from uuid import uuid4
from django.core.files.storage import default_storage
from os.path import splitext


def s3File(myfile, chosen_name=None):
    myfile2 = open(myfile.name, 'r')
    if chosen_name is not None:
        filename = chosen_name+'.png'
    else:
        extension = splitext(myfile.name)[1]
        filename = '1d_{filename}{ext}' .format(filename=str(uuid4()),ext=extension)
    #Try making a new file and sending that to s3
    s3file = default_storage.open(filename, 'w')
    s3file.write(myfile2.read())
    s3file.close()
    myfile2.close()
    return s3file

def outsourceJson(data,params):

    myjson = json.dumps({'data':data, 'parameters':params})
    datafilename = '1d_%s.json' % str(uuid4())
    datafile = open(datafilename,'wb')
    datafile.write(myjson)
    datafile.close()

    return s3File(datafile)
