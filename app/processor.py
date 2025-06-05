import threading
import time
from app.storage import ingestion_store, priority_queue, storage_lock
from app.models import BatchStatus
from app.utils import get_priority_value

PROCESSING_INTERVAL = 5  
BATCH_SIZE = 3

def simulate_external_fetch(id):
    time.sleep(1)
    return {"id": id, "data": "processed"}

def batch_worker():
    while True:
        time.sleep(PROCESSING_INTERVAL)
        with storage_lock:
            if not priority_queue:
                continue

            # sort by priority, then time
            sorted_queue = sorted(
                list(priority_queue),
                key=lambda x: (get_priority_value(x[0]), x[1])
            )
            priority_queue.clear()
            priority_queue.extend(sorted_queue)

            batch = priority_queue.popleft()
            _, _, ingestion_id, batch_info = batch

            batch_info['status'] = BatchStatus.TRIGGERED
        for id in batch_info['ids']:
            simulate_external_fetch(id)

        with storage_lock:
            batch_info['status'] = BatchStatus.COMPLETED

def start_background_worker():
    t = threading.Thread(target=batch_worker, daemon=True)
    t.start()
