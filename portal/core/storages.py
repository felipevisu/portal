from django.conf import settings
from django_tenants.utils import parse_tenant_config_path
from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    file_overwrite = False

    @property  # not cached like in parent of S3Boto3Storage class
    def location(self):
        _location = parse_tenant_config_path("media")
        return _location


class S3StaticStorage(S3Boto3Storage):
    file_overwrite = False
    location = "static"
