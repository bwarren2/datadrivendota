from uuid import uuid4
from django.core.files.storage import default_storage


def s3File(imagefile):
    imagefile2 = open(imagefile.name, 'r')

    #Try making a new file and sending that to s3
    s3file = default_storage.open('1d_%s.bmp' % str(uuid4()), 'w')
    s3file.write(imagefile2.read())
    s3file.close()
    imagefile2.close()

    return s3file
