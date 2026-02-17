from django.contrib import admin

from .models import ImportBatch, RawExcelRow
from .services import process_import_batch_sync
from .tasks import process_import_batch


class RawExcelRowInline(admin.TabularInline):
    model = RawExcelRow
    extra = 0
    readonly_fields = ("row_index", "raw_data")
    can_delete = False


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "source_file_name", "uploaded_by", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [RawExcelRowInline]
    readonly_fields = ("uploaded_by", "status", "error_message", "source_file_name", "created_at")
    fields = ("source_file", "source_file_name", "uploaded_by", "status", "error_message", "created_at")

    def save_model(self, request, obj, form, change):
        is_create = obj.pk is None
        if is_create and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        if obj.source_file and not obj.source_file_name:
            obj.source_file_name = obj.source_file.name

        super().save_model(request, obj, form, change)

        if is_create and obj.source_file:
            file_path = obj.source_file.path
            try:
                process_import_batch.delay(obj.id, file_path)
            except Exception:
                try:
                    process_import_batch_sync(obj.id, file_path)
                except Exception:
                    pass
