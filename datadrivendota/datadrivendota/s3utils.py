from storages.backends.s3boto import S3BotoStorage
import urllib
import urlparse

from django.contrib.staticfiles.storage import (
    CachedFilesMixin,
    # ManifestFilesMixin
)

from pipeline.storage import PipelineMixin

StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')
ParseS3BotoStorage = lambda: S3BotoStorage(location='processed_replay_parse')
# ,headers={'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}

# # CachedFilesMixin doesn't play well with Boto and S3. It over-quotes things,
# # causing erratic failures. So we subclass.
# # (See http://stackoverflow.com/questions/11820566/inconsistent-
# #    signaturedoesnotmatch-amazon-s3-with-django-pipeline-s3boto-and-st)


class PatchedCachedFilesMixin(CachedFilesMixin):
    def url(self, *a, **kw):
        s = super(PatchedCachedFilesMixin, self).url(*a, **kw)
        if isinstance(s, unicode):
            s = s.encode('utf-8', 'ignore')
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
        path = urllib.quote(path, '/%')
        qs = urllib.quote_plus(qs, ':&=')
        return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


# class S3PipelineManifestStorage(
#     PipelineMixin, ManifestFilesMixin, S3BotoStorage
# ):
#     pass


class S3PipelineCachedStorage(
    PipelineMixin, PatchedCachedFilesMixin, S3BotoStorage
):
    verbose = True

    # This is a hack from https://github.com/adamcharnock/django-pipeline-forgiving.
    def hashed_name(self, name, content=None):
        try:
            out = super(S3PipelineCachedStorage, self).hashed_name(
                name,
                content
            )
        except ValueError:
            # This means that a file could not be found.
            # normally this would cause a fatal error,
            # which seems rather excessive given that
            # some packages have missing files in their css all the time.
            out = name
            print "Had a hash error for {0}, using raw name".format(name)
        return out
