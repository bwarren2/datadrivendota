from io import BytesIO
import gzip

from django.utils.text import slugify
from django.core.files import File
from contextlib import closing

from datadrivendota.s3utils import ParseS3BotoStorage


def s3_parse(input_buf, filename):
    """ Move a file to s3. """

    output_buf = BytesIO()

    with gzip.GzipFile(
        fileobj=output_buf, mode='wb', filename='foo.json.gz'
    ) as f:
        f.write(input_buf.getvalue())

    output_buf.seek(0)

    with closing(ParseS3BotoStorage().open(filename, 'w')) as f:
        f.write(output_buf.read())


def fake_image(l):
    buff = BytesIO('11')
    buff.seek(0)
    filename = slugify(l.steam_id) + '_full.png'
    l.stored_image.save(filename, File(buff))
    return l
