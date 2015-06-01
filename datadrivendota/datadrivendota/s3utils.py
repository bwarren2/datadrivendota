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
    # packing = False
    # Sometimes there are packing failures.
    # If CSS is compiled and files don't need to be compressed, packing
    # can be false.
    # See also the todo in the readme.
