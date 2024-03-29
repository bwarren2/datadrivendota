from io import BytesIO

from django.utils.text import slugify
from django.core.files import File
from contextlib import closing

from datadrivendota.s3utils import ParseS3BotoStorage


def fake_image(l):
    buff = BytesIO('11')
    buff.seek(0)
    filename = slugify(l.steam_id) + '_full.png'
    l.stored_image.save(filename, File(buff))
    return l
