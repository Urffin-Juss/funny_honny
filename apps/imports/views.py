from rest_framework import serializers, viewsets

from apps.core.permissions import IsOwnerOrAdmin

from .models import ImportBatch
from .serializers import ImportBatchSerializer
from .services import process_import_batch_sync
from .tasks import process_import_batch


class ImportBatchViewSet(viewsets.ModelViewSet):
    queryset = ImportBatch.objects.prefetch_related("rows").all().order_by("-created_at")
    serializer_class = ImportBatchSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        batch = serializer.save(uploaded_by=self.request.user)
        if not batch.source_file:
            raise serializers.ValidationError({"source_file": "Excel file is required"})

        file_path = batch.source_file.path
        try:
            process_import_batch.delay(batch.id, file_path)
        except Exception:
            try:
                process_import_batch_sync(batch.id, file_path)
            except Exception:
                pass
