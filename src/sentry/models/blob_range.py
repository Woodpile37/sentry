from django.db import models
from django.utils import timezone

from sentry.db.models import Model, region_silo_only_model


@region_silo_only_model
class BlobRangeModel(Model):
    __include_in_export__ = False

    end = models.IntegerField()
    filename = models.CharField(max_length=32)
    key = models.CharField(max_length=64, db_index=True)
    start = models.IntegerField()
    dek = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        app_label = "sentry"
        db_table = "sentry_blob_range"
