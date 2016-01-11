from io import BytesIO
from django.utils.text import slugify
from django.core.files import File
from contextlib import closing

from datadrivendota.s3utils import ParseS3BotoStorage


def s3_parse(myfile, filename):
    """ Move a file to s3. """

    # Try making a new file and sending that to s3
    # s3_file = ParseS3BotoStorage().open(filename, 'w')

    with closing(ParseS3BotoStorage().open(filename, 'wb')) as f:
        f.write(myfile.read())
        # f._storage.headers['Content-Type'] = 'application/json'
        # f._storage.headers['Content-Encoding'] = 'gzip'


def fake_image(l):
    buff = BytesIO('11')
    buff.seek(0)
    filename = slugify(l.steam_id) + '_full.png'
    l.stored_image.save(filename, File(buff))
    return l
