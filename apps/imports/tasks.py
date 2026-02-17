from celery import shared_task

from .services import process_import_batch_sync


@shared_task
def process_import_batch(batch_id: int, file_path: str) -> None:
    process_import_batch_sync(batch_id=batch_id, file_path=file_path)
