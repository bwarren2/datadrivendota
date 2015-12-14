import boto
from boto.s3.key import Key

from django.conf import settings
from io import BytesIO
from django.utils.text import slugify
from django.core.files import File

from uuid import uuid4
from django.core.files.storage import default_storage


def s3_file(myfile, chosen_name=None):
    """ Move a file to s3. """
    if chosen_name is not None:
        filename = chosen_name + '.png'
    else:
        extension = 'json'
        filename = '1d_{filename}{ext}'.format(
            filename=str(uuid4()),
            ext=extension
        )

    # Try making a new file and sending that to s3
    s3file = default_storage.open(filename, 'w')
    s3file.write(myfile.read())
    s3file.close()
    return s3file


def fake_image(l):
    buff = BytesIO('11')
    _ = buff.seek(0)  # NOQA
    filename = slugify(l.steam_id) + '_full.png'
    l.stored_image.save(filename, File(buff))
    return l
