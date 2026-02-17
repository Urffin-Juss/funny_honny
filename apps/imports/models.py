from django.conf import settings
from django.db import models


class ImportBatchStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    FAILED = "failed", "Failed"
    DONE = "done", "Done"


class ImportBatch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="imports")
    source_file_name = models.CharField(max_length=255)
    source_file = models.FileField(upload_to="imports/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=ImportBatchStatus.choices, default=ImportBatchStatus.PENDING)
    error_message = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"ImportBatch #{self.pk} ({self.status})"


class RawExcelRow(models.Model):
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="rows")
    row_index = models.PositiveIntegerField()
    raw_data = models.JSONField()

    class Meta:
        unique_together = ("batch", "row_index")

    def __str__(self) -> str:
        return f"Batch {self.batch_id} row {self.row_index}"
