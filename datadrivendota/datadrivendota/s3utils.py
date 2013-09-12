from storages.backends.s3boto import S3BotoStorage

StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')

from staticfiles.storage import CachedFilesMixin
from pipeline.storage import PipelineMixin

class S3PipelineStorage(PipelineMixin, CachedFilesMixin, StaticRootS3BotoStorage):
     pass
